import itertools
import os
import re
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

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        doc_ref = self.submission_collection.document(submission_id)
        doc = doc_ref.get()
        if doc is None:
            raise Exception(f"There is no submission with the id: {submission_id}")
        document = doc.to_dict()
        document["id"] = doc.id
        return Submission(**document)


    def _fetch_user_shortlists(self, user_id: str) -> List:
        """Fetch shortlists for a user from Firestore."""
        shortlists = self.shortlist_collection.where("user_id", "==", user_id).get()
        if not shortlists:
            return []
        
        # Filter for recent shortlists (last 14 days)
        return [shortlist for shortlist in shortlists if shortlist.create_time > datetime.now(timezone.utc) - timedelta(days=30)]

    def _extract_property_ids_from_shortlists(self, shortlists: List) -> List[str]:
        """Extract all property IDs from shortlists."""
        property_ids = []
        for shortlist in shortlists:
            shortlist_data = shortlist.to_dict()
            properties = shortlist_data.get("properties", [])
            property_ids.extend([prop["property_id"] for prop in properties])
        return property_ids

    def _enrich_property_with_details(self, prop: Dict, property_data: Dict) -> Dict:
        """Enrich a property with details from property_data."""
        epc_url = None
        council_tax_band = None
        
        if property_data.get("property_details") and property_data["property_details"].get("location") and isinstance(property_data["property_details"]["location"], dict):
            epcs = property_data["property_details"].get("epcs")
            if epcs and "url" in epcs[0]:
                epc_url = epcs[0]["url"]
            council_tax = property_data["property_details"].get("localPropertyTax")
            if council_tax and "value" in council_tax:
                council_tax_band = council_tax["value"]

        # Enrich with property details
        prop.update({
            "address": property_data.get("address"),
            "created_at": property_data.get("created_at"),
            "postcode": property_data.get("postcode"),
            "price": property_data.get("price"),
            "num_bedrooms": property_data.get("num_bedrooms"),
            "num_bathrooms": property_data.get("num_bathrooms"),
            "stations": property_data.get("stations") or property_data.get('property_details', {}).get('nearestStations', []),
            "latitude": property_data.get("latitude"),
            "longitude": property_data.get("longitude"),
            "features": property_data.get("features"),
            "epc": epc_url,
            "council_tax_band": council_tax_band,
        })

        # Add sales info if available
        if property_data["property_details"].get("salesInfo"):
            prop.update({"tenure_type": property_data["property_details"].get("salesInfo").get("tenureType")})
            prop.update(property_data["property_details"].get("salesInfo"))
        
        # Add floorplans if available
        if property_data["property_details"].get("floorplans"):
            prop["floorplans"] = property_data["property_details"]["floorplans"]
        
        return prop

    def _enrich_property_with_extraction(self, prop: Dict, extraction: Dict) -> Dict:
        """Enrich a property with extraction data."""
        extraction_results = extraction.get("results", {})
        prop.update(extraction_results)
        return prop

    def _process_journey_data(self, prop: Dict) -> Dict:
        """Process and simplify journey data."""
        if prop.get("journey"):
            prop["journey"] = {"duration": prop["journey"]["duration"]}
        return prop

    def _build_enriched_shortlist(self, shortlists: List, properties: Dict[str, Dict], extractions: Dict[str, Dict]) -> List[Dict]:
        """Build the final enriched shortlist by combining all data sources."""
        seen_ids = set()
        all_shortlisted_properties = []
        
        for shortlist in shortlists:
            shortlist_data = shortlist.to_dict()
            for prop in shortlist_data.get("properties", []):
                property_id = prop["property_id"]
                
                if property_id in seen_ids:
                    continue
                
                # Enrich with property details
                if property_id in properties:
                    prop = self._enrich_property_with_details(prop, properties[property_id])
                
                # Enrich with extraction data
                if property_id in extractions:
                    prop = self._enrich_property_with_extraction(prop, extractions[property_id])
                
                # Process journey data
                prop = self._process_journey_data(prop)
                
                all_shortlisted_properties.append(prop)
                seen_ids.add(property_id)
        
        return all_shortlisted_properties

    def get_shortlists_by_user_id(self, user_id: str) -> List[Dict]:
        """Get enriched shortlists for a user."""
        # Fetch shortlists
        shortlists = self._fetch_user_shortlists(user_id)
        if not shortlists:
            return []

        # Extract property IDs
        property_ids = self._extract_property_ids_from_shortlists(shortlists)

        # Fetch properties and extractions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            properties_future = executor.submit(self._fetch_properties, property_ids)
            extractions_future = executor.submit(self._fetch_extractions, property_ids)
            
            properties = properties_future.result()
            extractions = extractions_future.result()
        
        # Build enriched shortlist
        result = self._build_enriched_shortlist(shortlists, properties, extractions)
        
        return result

    def get_submissions_by_user_id(self, user_id: str) -> List[Dict]:
        """Fetch all submissions for a specific user.
        
        Args:
            user_id (str): The ID of the user to fetch submissions for
            
        Returns:
            List[Dict]: A list of submission documents, each containing the submission data
        """
        try:
            # Query submissions collection for the user_id
            submissions = self.submission_collection.where("user_id", "==", user_id).get()
            
            if not submissions:
                return []
            
            # Convert Firestore documents to dictionaries
            submission_list = []
            for submission in submissions:
                submission_data = submission.to_dict()
                submission_data["id"] = submission.id  # Add the document ID
                submission_list.append(submission_data)
            
            return submission_list
            
        except Exception as e:
            print(f"Error fetching submissions for user {user_id}: {str(e)}")
            return []

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
    details = firestore.fetch_user_details_by_email('example@example.com')
    print(details)
    print(details.get("password", ""))
    # all_shortlisted_properties = firestore.get_shortlists_by_user_id("hIk6crfW5BncLCYK8fIR")
    # print(all_shortlisted_properties)
    # save_json(all_shortlisted_properties, "shortlist_new.json")
    # submissions = firestore.get_submissions_by_user_id("hIk6crfW5BncLCYK8fIR")
