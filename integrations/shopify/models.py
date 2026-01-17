"""
Shopify data models
"""
from pydantic import BaseModel
from typing import List, Optional


class ShopifyImage(BaseModel):
    id: int
    src: str
    alt: Optional[str] = None


class ShopifyVariant(BaseModel):
    id: int
    title: str
    price: str
    sku: Optional[str] = None
    inventory_quantity: int = 0


class ShopifyProduct(BaseModel):
    id: int
    title: str
    handle: str
    description: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = []
    images: List[ShopifyImage] = []
    variants: List[ShopifyVariant] = []
    
    @property
    def primary_image(self) -> Optional[str]:
        return self.images[0].src if self.images else None
    
    @property
    def price(self) -> str:
        return self.variants[0].price if self.variants else "0.00"


class ShopifyCollection(BaseModel):
    id: int
    title: str
    handle: str
    description: Optional[str] = None
