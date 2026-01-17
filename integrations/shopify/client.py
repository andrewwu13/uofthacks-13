"""
Shopify API client
"""
import httpx
from typing import List, Optional


class ShopifyClient:
    """
    Client for Shopify Admin and Storefront APIs.
    Handles product fetching and payment through Shopify.
    """
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        store_url: str = "",
        api_version: str = "2024-01",
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.store_url = store_url
        self.api_version = api_version
        self.client = httpx.AsyncClient()
    
    @property
    def base_url(self) -> str:
        return f"https://{self.store_url}/admin/api/{self.api_version}"
    
    @property
    def headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.api_secret,
            "Content-Type": "application/json",
        }
    
    async def get_products(
        self,
        limit: int = 50,
        collection_id: Optional[str] = None,
    ) -> List[dict]:
        """Fetch products from Shopify"""
        url = f"{self.base_url}/products.json"
        params = {"limit": limit}
        if collection_id:
            params["collection_id"] = collection_id
        
        response = await self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("products", [])
    
    async def get_product(self, product_id: str) -> Optional[dict]:
        """Fetch single product"""
        url = f"{self.base_url}/products/{product_id}.json"
        response = await self.client.get(url, headers=self.headers)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("product")
    
    async def get_collections(self) -> List[dict]:
        """Fetch product collections"""
        url = f"{self.base_url}/custom_collections.json"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("custom_collections", [])
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


shopify_client = ShopifyClient()
