from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

class CoreBenefit(ORMBase):
    id: Optional[UUID] = None 
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    tab_label: str
    content_title: str
    content_description: Optional[str] = None 
    values: Optional[List[str]] = [] 
    sequence: int 

class CoreValue(ORMBase):
    id: Optional[UUID] = None
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    icon: Optional[str] = None
    icon_title: Optional[str] = None
    icon_description: Optional[str] = None
    sequence: Optional[int] = None

class IndustryItem(ORMBase):
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    sequence: Optional[int] = None

class IndustrySection(ORMBase):
    id: Optional[UUID] = None
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    industries: List[IndustryItem] = []

class CoreSolutionItem(ORMBase):
    id: Optional[UUID] = None
    icon: Optional[str] = None
    title: str
    description: Optional[str] = None 
    sequence: Optional[int] = None

class CoreSolution(ORMBase):
    id: Optional[UUID] = None
    section_title: Optional[str] = None
    section_subtitle: Optional[str] = None
    items: List[CoreSolutionItem] = []

class FAQItem(ORMBase):
    id: Optional[UUID] = None
    question: str
    answer: str
    sequence: Optional[int] = None

class SocialTrustItem(ORMBase):
    id: UUID
    name: str
    logo_url: str
    sequence: int

class Solution(ORMBase):
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

    core_benefits: List[CoreBenefit] = [] 
    core_values: List[CoreValue] = []
    industry_section: Optional[IndustrySection] = None
    core_solution: Optional[CoreSolution] = None
    faqs: List[FAQItem] = []
    trusted_by: List[SocialTrustItem] = []

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None