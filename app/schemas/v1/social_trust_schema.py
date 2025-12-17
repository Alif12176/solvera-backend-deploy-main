from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True

class SocialTrustItem(ORMBase):
    id: UUID 
    name: str
    logo_url: str
    sequence: Optional[int] = 0

class SocialTrustSection(BaseModel):
    section_title: str
    items: List[SocialTrustItem] = []