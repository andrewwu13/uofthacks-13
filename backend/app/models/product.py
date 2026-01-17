from pydantic import BaseModel, HttpUrl
from typing import Optional

class Product(BaseModel):
    id: int
    store_domain: str
    title: str
    handle: str
    url: HttpUrl
    price: str
    currency: str
    image: Optional[HttpUrl] = None
    vendor: str
    description: Optional[str] = None
