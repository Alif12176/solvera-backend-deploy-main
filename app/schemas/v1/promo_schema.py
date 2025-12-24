from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class PromoBadge(BaseModel):
    line1: str
    line2: str
    label: str

class PromoBase(BaseModel):
    is_active: bool = False
    title: str
    subtitle: Optional[str] = None
    cta_label: Optional[str] = None
    cta_link: Optional[str] = None
    promo_badge_line1: Optional[str] = None
    promo_badge_line2: Optional[str] = None
    promo_badge_label: Optional[str] = None
    features: Optional[List[str]] = None
    idle_bg_color: Optional[str] = None
    scroll_bg_color: Optional[str] = None
    illustration_url: Optional[str] = None
    image_url: Optional[str] = None

class PromoCreate(PromoBase):
    pass

class PromoUpdate(BaseModel):
    is_active: Optional[bool] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    cta_label: Optional[str] = None
    cta_link: Optional[str] = None
    promo_badge_line1: Optional[str] = None
    promo_badge_line2: Optional[str] = None
    promo_badge_label: Optional[str] = None
    features: Optional[List[str]] = None
    idle_bg_color: Optional[str] = None
    scroll_bg_color: Optional[str] = None
    illustration_url: Optional[str] = None
    image_url: Optional[str] = None

class PromoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    isActive: bool
    title: str
    subtitle: Optional[str]
    ctaLabel: Optional[str]
    ctaLink: Optional[str]
    promoBadge: PromoBadge
    features: List[str]
    idleBg: Optional[str]
    scrollBg: Optional[str]
    illustrationUrl: Optional[str]
    image: Optional[str]

    @classmethod
    def from_orm_model(cls, obj):
        return cls(
            isActive=obj.is_active,
            title=obj.title,
            subtitle=obj.subtitle,
            ctaLabel=obj.cta_label,
            ctaLink=obj.cta_link,
            promoBadge=PromoBadge(
                line1=obj.promo_badge_line1 or "",
                line2=obj.promo_badge_line2 or "",
                label=obj.promo_badge_label or ""
            ),
            features=obj.features or [],
            idleBg=obj.idle_bg_color,
            scrollBg=obj.scroll_bg_color,
            illustrationUrl=obj.illustration_url,
            image=obj.image_url
        )
