from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

class CategoryItem(ORMBase):
    id: int
    name: str

class AuthorItem(ORMBase):
    id: int
    name: str

class ArticleSchema(ORMBase):
    id: UUID
    title: str
    slug: str
    summary: Optional[str]
    content: str
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    publisher: Optional[AuthorItem] = None
    categories: List[CategoryItem] = []

class PaginatedArticleResponse(BaseModel):
    items: List[ArticleSchema]
    page: int
    limit: int
    has_more: bool

class CategoryListResponse(BaseModel):
    items: List[CategoryItem]
    count: int