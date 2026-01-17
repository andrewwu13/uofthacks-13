import json
import os
from typing import List
from app.models.product import Product

class ProductService:
    def __init__(self, products_file: str = "500_products.json"):
        self.products_file = products_file

    def get_products_for_session(self, session_id: str) -> List[dict]:
        """Get products for a specific session. Currently returns all products,
        but can be extended to filter based on user preferences.
        
        # TODO: Fetch persisted preferences for session_id from DB
        # TODO: Filter or re-rank products based on those preferences
        """
        if not os.path.exists(self.products_file):
            return []
        
        with open(self.products_file, "r", encoding="utf-8") as f:
            return json.load(f)

product_service = ProductService()
