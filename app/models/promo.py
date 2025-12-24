from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from app.db.base import Base

class Promo(Base):
    __tablename__ = "promos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    is_active = Column(Boolean, default=False)
    
    title = Column(Text, nullable=False)
    subtitle = Column(Text, nullable=True)
    
    cta_label = Column(String, nullable=True)
    cta_link = Column(String, nullable=True)
    
    promo_badge_line1 = Column(String, nullable=True)
    promo_badge_line2 = Column(String, nullable=True)
    promo_badge_label = Column(String, nullable=True)
    
    features = Column(JSON, nullable=True)
    
    idle_bg_color = Column(String, nullable=True)
    scroll_bg_color = Column(String, nullable=True)
    
    illustration_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __str__(self):
        return self.title
