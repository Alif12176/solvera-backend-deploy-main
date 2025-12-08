from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

class CategoryItem(BaseModel):
    id: int
    name: str

class AuthorItem(BaseModel):
    id: int
    name: str

class ArticleSchema(BaseModel):
    id: UUID
    title: str
    slug: str
    summary: Optional[str]
    content: str
    image_url: Optional[HttpUrl] = None
    published_at: Optional[datetime] = None
    publisher: Optional[AuthorItem] = None
    categories: List[CategoryItem] = []
