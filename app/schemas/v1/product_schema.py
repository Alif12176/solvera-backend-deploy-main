from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union, Literal, Any
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

class TabFeatureItem(ORMBase):
    id: UUID
    type: Literal["tab_item"] = "tab_item"

    tab_label: str
    
    title: str = Field(..., alias="content_title") 
    description: Optional[str] = Field(None, alias="content_description")
    benefits: Optional[List[str]] = []
    sequence: int

class ImageFeatureItem(ORMBase):
    id: UUID
    type: Literal["image_card"] = "image_card"

    image_url: str
    title: str = Field(..., alias="content_title")
    description: Optional[str] = Field(None, alias="content_description")
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

class SocialTrustItem(ORMBase):
    id: Optional[UUID] = None
    name: Optional[str] = None
    logo_url: str
    sequence: Optional[int] = 0

class ProductSchema(ORMBase):
    id: UUID 
    slug: str
    name: str
    category: Optional[str] = None
    
    layout_type: str 

    hero_title: str
    hero_subtitle: Optional[str] = None
    hero_image: Optional[str] = Field(None, alias="hero_image")
    
    cta_primary_text: Optional[str] = None
    cta_secondary_text: Optional[str] = None
    cta_image: Optional[str] = None
    
    features: Union[List[TabFeatureItem], List[ImageFeatureItem]] = []
    social_trusts: List[SocialTrustItem] = []
    why_us: List[WhyUsCardItem] = []
    faqs: List[FAQItem] = []
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    @classmethod
    def transform_features_based_on_layout(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data

        layout = getattr(data, 'layout_type', 'default')
        raw_features = getattr(data, 'features', [])
        sorted_features = sorted(raw_features, key=lambda x: x.sequence or 0)

        cleaned_features = []

        for f in sorted_features:
            base_item = {
                "id": f.id,
                "sequence": f.sequence,
                "content_title": f.content_title,
                "content_description": f.content_description,
                "benefits": f.benefits
            }

            if layout == 'default':
                cleaned_features.append({
                    **base_item,
                    "type": "tab_item",
                    "tab_label": f.tab_label or "Untitled Tab"

                })
            
            elif layout == 'feature_list':
                cleaned_features.append({
                    **base_item,
                    "type": "image_card",
                    "image_url": f.image_url or "" 
                })

        product_dict = {
            "id": data.id,
            "slug": data.slug,
            "name": data.name,
            "category": data.category,
            "layout_type": layout,
            "hero_title": data.hero_title,
            "hero_subtitle": data.hero_subtitle,
            "hero_image": data.hero_image,
            "cta_primary_text": data.cta_primary_text,
            "cta_secondary_text": data.cta_secondary_text,
            "cta_image": data.cta_image,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "why_us": data.why_us, 
            "faqs": data.faqs,
            "features": cleaned_features
        }
        
        return product_dict

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class ProductListResponse(BaseModel):
    items: List[ProductSchema]
    meta: PaginationMeta