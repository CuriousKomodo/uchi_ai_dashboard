import itertools
import os
from typing import List, Dict, Optional
import time
import concurrent.futures
from cachetools import TTLCache, LRUCache, cached, TTLCache
from collections import defaultdict

from google.cloud import firestore
from datetime import datetime, timezone, timedelta

from google.cloud.firestore_v1 import FieldFilter
from pydantic import ValidationError

from custom_exceptions import NoUserFound
from schema.firestore import Submission
from utils.cache import CacheManager
from utils.common import save_json

dir_path = os.path.dirname(os.path.realpath(__file__))
credential_info_path = f"{dir_path}/firestore_key.json"


class FireStore:
    def __init__(self, credential_info: Optional[Dict] = None):
        if credential_info:
            self.db = firestore.Client.from_service_account_info(credential_info)
        else:
            self.db = firestore.Client.from_service_account_json(credential_info_path)
        self.users_collection = self.db.collection('users')
        self.submission_collection = self.db.collection('submissions')
        self.initial_screening_collection = self.db.collection('initial_screening')
        self.property_collection = self.db.collection('properties')
        self.shortlist_collection = self.db.collection('shortlist')
        self.extraction_collection = self.db.collection('extraction')
        
        # Initialize cache manager
        self.cache_manager = CacheManager()

    @cached(cache=TTLCache(maxsize=1000, ttl=300))
    def _fetch_property(self, property_id: str) -> Optional[Dict]:
        """Fetch a single property with caching."""
        try:
            # Check if in cache
            if property_id in self.cache_manager.get_property_cache():
                self.cache_manager._update_cache_stats('property', hit=True)
                return self.cache_manager.get_property_cache()[property_id]
            
            # If not in cache, fetch from Firestore
            self.cache_manager._update_cache_stats('property', hit=False)
            doc = self.property_collection.where("id", "==", property_id).get()
            if doc:
                return doc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error fetching property {property_id}: {str(e)}")
            return None

    @cached(cache=TTLCache(maxsize=1000, ttl=300))
    def _fetch_extraction(self, property_id: str) -> Optional[Dict]:
        """Fetch a single extraction with caching."""
        try:
            # Check if in cache
            if property_id in self.cache_manager.get_extraction_cache():
                self.cache_manager._update_cache_stats('extraction', hit=True)
                return self.cache_manager.get_extraction_cache()[property_id]
            
            # If not in cache, fetch from Firestore
            self.cache_manager._update_cache_stats('extraction', hit=False)
            doc = self.extraction_collection.where("property_id", "==", property_id).get()
            if doc:
                return doc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error fetching extraction {property_id}: {str(e)}")
            return None


    def _fetch_properties(self, property_ids: List[str]) -> Dict[str, Dict]:
        """Fetch properties in parallel."""
        properties = {}
        
        # Fetch properties in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_property = {executor.submit(self._fetch_property, pid): pid for pid in property_ids}
            for future in concurrent.futures.as_completed(future_to_property):
                property_id = future_to_property[future]
                try:
                    property_data = future.result()
                    if property_data:
                        properties[property_id] = property_data
                except Exception as e:
                    print(f"Error fetching property {property_id}: {str(e)}")
        
        return properties

    def _fetch_extractions(self, property_ids: List[str]) -> Dict[str, Dict]:
        """Fetch extractions in parallel."""
        extractions = {}
        
        # Fetch extractions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_extraction = {executor.submit(self._fetch_extraction, pid): pid for pid in property_ids}
            for future in concurrent.futures.as_completed(future_to_extraction):
                property_id = future_to_extraction[future]
                try:
                    extraction_data = future.result()
                    if extraction_data:
                        extractions[property_id] = extraction_data
                except Exception as e:
                    print(f"Error fetching extraction {property_id}: {str(e)}")
        
        return extractions

    def insert_submission(self, results):
        # Create the new user
        user_fields = {
            "email": results["email"],
            "first_name": results["first_name"],
            'created_at': datetime.now(),
        }
        # Do check to see if the user already exists.
        _, record = self.users_collection.add(user_fields)
        user_id = record.path.split("/")[-1]

        # Store the submission
        self.submission_collection.add({
            "user_id": user_id,
            'email': results["email"],
            'content': results,
            'created_at': datetime.now()
        })

    def insert_extraction(self, property_id, extraction):
        self.db.collection('extraction').add({
            "property_id": property_id,
            "results": extraction,
            'created_at': datetime.now()
        })

    def insert_property(self, property_id, property_details):
        extracted_metadata = {
            "id": property_id,
            "num_bedrooms": property_details.get("bedrooms"),
            "num_bathrooms": property_details.get("bathrooms"),
            "price": int(property_details.get("analyticsInfo").get("price")),
            "postcode": property_details.get("postcode"),
            "address": property_details.get("address"),
            "stations": property_details.get("stations"),
            "features": property_details.get("keyFeatures"),
        }
        extracted_metadata.update({"property_details": property_details, 'created_at': datetime.now()})
        self.db.collection('properties').add(extracted_metadata)

    def list_all_users(self) -> List[Dict]:
        users_stream = self.users_collection.stream()
        users = []
        for doc in users_stream:
            print('{} => {}'.format(doc.id, doc.to_dict()))
            users.append(doc.to_dict())
        return users

    def list_all_submissions(self) -> List[Submission]:
        submissions_stream = self.submission_collection.stream()
        # query = self.submission_collection.where('created_at', '>', "")
        submissions = []
        for doc in submissions_stream:
            try:
                submission = Submission(**doc.to_dict())
                if submission.is_active:
                    submissions.append(submission)
            except ValidationError as e:
                continue
        return submissions

    def get_list_of_properties_based_on_submission(self, submission: Submission, days_added: int = 3) -> List[Dict]:
        properties_ref = self.db.collection('properties')

        filters = [
            firestore.FieldFilter('price', '<', submission.content.max_price * 1000),
            firestore.FieldFilter('created_at', '>', datetime.now(timezone.utc) - timedelta(days=days_added + 1))
        ]
        query = properties_ref.where(filter=filters[0]).where(filter=filters[1])

        output = query.stream()
        properties = [doc for doc in output if doc.to_dict()['num_bedrooms'] > submission.content.num_bedrooms - 1]

        # if submission.content.num_bathrooms:
        #     query = query.where('num_bathrooms', '>', submission.content.num_bathrooms-1)
        extraction_ref = self.db.collection('extraction')
        properties_with_extraction = []
        for doc in properties:
            property_info = doc.to_dict()
            property_id = property_info["id"]
            property_info.pop("property_details")
            extraction_query = extraction_ref.where(
                filter=FieldFilter('property_id', '==', property_id)
            )

            extraction_output = extraction_query.stream()
            extractions = [(extraction.id, extraction.to_dict()) for extraction in extraction_output]
            if extractions:
                sorted_extractions = sorted(extractions, key=lambda tup: tup[1]['created_at'], reverse=True)
                property_info["extraction_id"] = sorted_extractions[0][0]
                property_info["extraction"] = sorted_extractions[0][1]
                properties_with_extraction.append(property_info)
        return properties_with_extraction

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        doc_ref = self.submission_collection.document(submission_id)
        doc = doc_ref.get()
        if doc is None:
            raise Exception(f"There is no submission with the id: {submission_id}")
        document = doc.to_dict()
        document["id"] = doc.id
        return Submission(**document)

    def insert_shortlist(self, properties: List[Dict], submission_id: str, ):
        self.db.collection('shortlist').add({
            "properties": properties,
            "submission_id": submission_id,
            'created_at': datetime.now()
        })

    def get_shortlists_by_user_id(self, user_id: str) -> List[Dict]:
        # Query for shortlists
        shortlists = self.shortlist_collection.where("user_id", "==", user_id).get()
        
        if not shortlists:
            return []
        
        # Get all property IDs
        property_ids = []
        for shortlist in shortlists:
            shortlist_data = shortlist.to_dict()
            properties = shortlist_data.get("properties", [])
            property_ids.extend([prop["property_id"] for prop in properties])
        
        # Fetch properties and extractions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            properties_future = executor.submit(self._fetch_properties, property_ids)
            extractions_future = executor.submit(self._fetch_extractions, property_ids)
            
            properties = properties_future.result()
            extractions = extractions_future.result()
        
        # Combine the data
        all_shortlisted_properties = []
        for shortlist in shortlists:
            shortlist_data = shortlist.to_dict()
            for prop in shortlist_data.get("properties", []):
                property_id = prop["property_id"]
                if property_id in properties:
                    property_data = properties[property_id]
                    prop.update({
                        "address": property_data.get("address"),
                        "postcode": property_data.get("postcode"),
                        "price": property_data.get("price"),
                        "num_bedrooms": property_data.get("num_bedrooms"),
                        "stations": property_data.get("stations")
                    })
                    if property_data["property_details"].get("salesInfo"):
                        prop.update(property_data["property_details"].get("salesInfo"))
                    if property_data["property_details"]["floorplans"]:
                        prop["floorplans"] = property_data["property_details"]["floorplans"]

                if property_id in extractions:
                    prop.update(extractions[property_id].get("results", {}))
                
                all_shortlisted_properties.append(prop)
        
        return all_shortlisted_properties

    def fetch_user_details_by_email(self, email) -> Dict:
        users = self.db.collection('users').where('email', '==', email).get()
        if not users:
            raise NoUserFound(f"There is no user with the email: {email}")
        else:
            user_details = users[0].to_dict()
            user_details.update({"user_id":users[0].id})
        return user_details


if __name__ == '__main__':
    firestore = FireStore()
    # submissions = firestore.list_all_submissions()
    # firestore.fetch_user_details_by_email('hu.kefei@yahoo.co.uk')
    all_shortlisted_properties = firestore.get_shortlists_by_user_id("hIk6crfW5BncLCYK8fIR")
    save_json(all_shortlisted_properties, "shortlist_new.json")
