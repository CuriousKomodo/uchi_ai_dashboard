import requests
import urllib.parse
import unittest
from typing import Dict

class TestURLGeneration(unittest.TestCase):
    def setUp(self):
        self.test_properties = [
            {
                "property_id": "123",
                "address": "123 Main St",
                "price": "500000",
                "bedrooms": "3"
            },
            {
                "property_id": "456",
                "address": "456 Park Ave, Apt #4B",
                "price": "750000",
                "bedrooms": "2"
            },
            {
                "property_id": "789",
                "address": "789 Ocean View Dr, 2nd Floor",
                "price": "1200000",
                "bedrooms": "4"
            }
        ]

    def generate_chat_url(self, prop: Dict) -> str:
        """Generate the chat URL for a property."""
        return (
            f"/ask_ai/"
            f"{prop['property_id']}/"
            f"{requests.utils.quote(prop['address'])}/"
            f"{prop['price']}/"
            f"{prop['bedrooms']}"
        )

    def parse_chat_url(self, url: str) -> Dict:
        """Parse a chat URL into property context."""
        parts = url.strip("/").split("/")
        if len(parts) < 4:
            return {
                "property_id": "",
                "address": "",
                "price": "",
                "bedrooms": ""
            }
        
        return {
            "property_id": parts[1],
            "address": urllib.parse.unquote(parts[2]),
            "price": parts[3],
            "bedrooms": parts[4] if len(parts) > 4 else ""
        }

    def test_url_generation(self):
        """Test URL generation for various property types."""
        for prop in self.test_properties:
            url = self.generate_chat_url(prop)
            parsed = self.parse_chat_url(url)
            
            # Test that all properties are preserved
            self.assertEqual(parsed["property_id"], prop["property_id"])
            self.assertEqual(parsed["address"], prop["address"])
            self.assertEqual(parsed["price"], prop["price"])
            self.assertEqual(parsed["bedrooms"], prop["bedrooms"])
            
            # Test URL format
            self.assertTrue(url.startswith("/ask_ai/"))
            self.assertEqual(len(url.split("/")), 6)  # /ask_ai/id/address/price/bedrooms

    def test_special_characters(self):
        """Test URL handling of special characters."""
        special_cases = [
            {
                "property_id": "123",
                "address": "123 Main St, #4B & Co.",
                "price": "500000",
                "bedrooms": "3"
            },
            {
                "property_id": "456",
                "address": "456 Park Ave, Apt 2/3",
                "price": "750000",
                "bedrooms": "2"
            },
            {
                "property_id": "789",
                "address": "789 Ocean View Dr, Floor 2½",
                "price": "1200000",
                "bedrooms": "4"
            }
        ]
        
        for prop in special_cases:
            url = self.generate_chat_url(prop)
            parsed = self.parse_chat_url(url)
            
            # Test that special characters are preserved
            self.assertEqual(parsed["address"], prop["address"])
            
            # Test that URL is properly encoded
            self.assertNotIn(" ", url)
            self.assertNotIn("&", url)
            self.assertNotIn("/", url[url.find(prop["address"]):])

    def test_missing_parameters(self):
        """Test handling of missing parameters."""
        incomplete_urls = [
            "/ask_ai/",
            "/ask_ai/123",
            "/ask_ai/123/456%20Main%20St",
            "/ask_ai/123/456%20Main%20St/500000"
        ]
        
        for url in incomplete_urls:
            parsed = self.parse_chat_url(url)
            self.assertEqual(parsed["property_id"], "" if len(url.strip("/").split("/")) < 2 else url.strip("/").split("/")[1])

def print_test_cases():
    """Print example URLs for manual verification."""
    test_cases = [
        {
            "property_id": "123",
            "address": "123 Main St",
            "price": "500000",
            "bedrooms": "3"
        },
        {
            "property_id": "456",
            "address": "456 Park Ave, Apt #4B",
            "price": "750000",
            "bedrooms": "2"
        },
        {
            "property_id": "789",
            "address": "789 Ocean View Dr, 2nd Floor",
            "price": "1200000",
            "bedrooms": "4"
        }
    ]
    
    print("\nExample URLs:")
    print("-" * 50)
    for prop in test_cases:
        url = TestURLGeneration().generate_chat_url(prop)
        print(f"Property: {prop['address']}")
        print(f"Generated URL: {url}")
        print(f"Decoded address: {urllib.parse.unquote(url.split('/')[3])}")
        print("-" * 50)

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Print example URLs
    print_test_cases() 