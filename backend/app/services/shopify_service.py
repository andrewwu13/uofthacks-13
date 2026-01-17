"""
Shopify API integration service
"""
from typing import List, Optional
from app.models.events import ProductModel
import httpx


class ShopifyService:
    """Service for Shopify API integration"""
    
    def __init__(self, api_key: str = "", api_secret: str = "", store_url: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.store_url = store_url
        self.client = httpx.AsyncClient()
    
    async def list_products(
        self,
        limit: int = 20,
        page: int = 1,
        category: Optional[str] = None,
    ) -> List[ProductModel]:
        """Fetch products from Shopify"""
        # TODO: Implement Shopify API call
        return []
    
    async def get_product(self, product_id: str) -> Optional[ProductModel]:
        """Fetch single product from Shopify"""
        # TODO: Implement Shopify API call
        return None
    
    async def search_products(self, query: str, limit: int = 20) -> List[ProductModel]:
        """Search products in Shopify"""
        # TODO: Implement Shopify API call
        return []
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


shopify_service = ShopifyService()
