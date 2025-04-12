import itertools
import os
from typing import List, Dict, Optional

from google.cloud import firestore
from datetime import datetime, timezone, timedelta

from google.cloud.firestore_v1 import FieldFilter
from pydantic import ValidationError

from custom_exceptions import NoUserFound
from schema.firestore import Submission

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

    def get_shortlist_properties(
            self,
            shortlist_id: str,
            property_included: bool = True,
            extraction_included: bool = False
    ) -> List[Dict]:
        doc_ref = self.shortlist_collection.document(shortlist_id)
        doc = doc_ref.get()

        # Only filter for the top ones, and join with the property details
        filtered_shortlist = []
        for shortlist_item in doc.to_dict()["properties"]:
            if property_included:
                property_id = shortlist_item["property_id"]
                query = self.property_collection.where("id", "==", property_id)  # Assuming "id" is a field in the documents
                results = query.stream()
                property = []
                for doc in results:
                    property.append(doc.to_dict())

                if property:
                    shortlist_item["address"] = property[0].get("address")
                    shortlist_item["postcode"] = property[0].get("postcode")
                    shortlist_item["price"] = property[0].get("price")
                    shortlist_item["num_bedrooms"] = property[0].get("num_bedrooms")
                    shortlist_item["stations"] = property[0].get("stations")

                if extraction_included:
                    extraction_id = shortlist_item["extraction_id"]
                    extraction_ref = self.extraction_collection.document(extraction_id)
                    extraction = extraction_ref.get().to_dict()
                    shortlist_item.update(extraction["results"])

                filtered_shortlist.append(shortlist_item)
        return filtered_shortlist


    def get_shortlists_by_user_id(self, user_id: str) -> List[Dict]:
        shortlists = self.shortlist_collection.where("user_id", "==", user_id).get()
        shortlists.sort(key=lambda x: x.create_time, reverse=True)
        all_shortlisted_properties = []

        for shortlist in shortlists:
            shortlist_properties = self.get_shortlist_properties(shortlist_id=shortlist.id, extraction_included=True)
            all_shortlisted_properties.extend(shortlist_properties)
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
    firestore.fetch_user_details_by_email('hu.kefei@yahoo.co.uk')
    firestore.get_shortlists_by_user_id("uUjGIe4uaSIK7m0skEwV")
