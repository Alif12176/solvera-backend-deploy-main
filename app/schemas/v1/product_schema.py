from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

class FeatureTabItem(ORMBase):
    id: Optional[UUID] = None 
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    tab_label: str
    content_title: str
    content_description: Optional[str] = None 
    image_url: Optional[str] = None
    benefits: Optional[List[str]] = [] 
    sequence: int 

class WhyUsCardItem(ORMBase):
    id: Optional[UUID] = None
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    icon: Optional[str] = None
    card_label: Optional[str] = None
    sequence: Optional[int] = None

class FAQItem(ORMBase):
    id: Optional[UUID] = None
    question: str
    answer: str
    sequence: Optional[int] = None

class ProductSchema(ORMBase):
    id: UUID 
    slug: str
    name: str
    category: Optional[str] = None
    
    hero_title: str
    hero_subtitle: Optional[str] = None
    hero_image: Optional[str] = None
    
    cta_primary_text: Optional[str] = None
    cta_secondary_text: Optional[str] = None
    cta_image: Optional[str] = None
    
    features: List[FeatureTabItem] = [] 
    why_us: List[WhyUsCardItem] = []
    faqs: List[FAQItem] = []
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class ProductListResponse(BaseModel):
    items: List[ProductSchema]
    meta: PaginationMeta