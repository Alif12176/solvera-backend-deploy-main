from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class CategoryItem(BaseModel):
    id: int = Field(..., description="Unique Integer ID for category")
    name: str = Field(..., description="Display name of the category")
    slug: str = Field(..., description="URL-friendly identifier for filtering")

    class Config:
        from_attributes = True 

class AuthorItem(BaseModel):
    id: int = Field(..., description="Unique Integer ID for author")
    name: str = Field(..., description="Full name of the author")

    class Config:
        from_attributes = True

class ArticleSchema(BaseModel):
    id: UUID = Field(..., description="Unique UUID for the article")
    title: str = Field(..., description="Headline title of the article")
    slug: str = Field(..., description="URL-friendly slug for routing")
    summary: Optional[str] = Field(None, description="Short excerpt for list views")
    content: str = Field(..., description="Full HTML or Markdown content")
    image_url: Optional[str] = Field(None, description="Cover image URL")
    published_at: Optional[datetime] = Field(None, description="ISO datetime of publication")
    publisher: Optional[AuthorItem] = Field(None, description="Author details")
    categories: List[CategoryItem] = Field([], description="List of associated categories")

    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    items: List[ArticleSchema]
    total: int
    page: int
    limit: int