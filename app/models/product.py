from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    slug = Column(String, unique=True, index=True) 
    name = Column(Text, nullable=False)
    
    hero_title = Column(Text, nullable=False)
    hero_subtitle = Column(Text, nullable=True)
    
    hero_image = Column(String, nullable=True) 
    cta_primary_text = Column(String, nullable=True)
    cta_secondary_text = Column(String, nullable=True)
    cta_image = Column(String, nullable=True)

    category = Column(String, index=True, nullable=True) 
    layout_type = Column(String, default='default', nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    features = relationship("ProductFeature", back_populates="product", order_by="ProductFeature.sequence", cascade="all, delete-orphan")
    why_us = relationship("ProductWhyUs", back_populates="product", order_by="ProductWhyUs.sequence", cascade="all, delete-orphan")
    faqs = relationship("ProductFAQ", back_populates="product", order_by="ProductFAQ.sequence", cascade="all, delete-orphan")
    social_trusts = relationship("ProductSocialTrust", back_populates="product", order_by="ProductSocialTrust.sequence", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class ProductFeature(Base):
    __tablename__ = "product_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    section_title = Column(Text, nullable=True)     
    section_subtitle = Column(Text, nullable=True)  
    tab_label = Column(Text, nullable=True)        
    
    content_title = Column(Text, nullable=False)    
    content_description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    benefits = Column(JSON, nullable=True)        
    sequence = Column(Integer, default=0, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="features")

    def __str__(self):
        return self.content_title

class ProductWhyUs(Base):
    __tablename__ = "product_why_us"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    section_title = Column(Text, nullable=True)
    section_subtitle = Column(Text, nullable=True)
    card_label = Column(Text, nullable=True) 
    
    icon = Column(String, nullable=True)     

    sequence = Column(Integer, default=0, index=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="why_us")

    def __str__(self):
        return self.card_label or self.section_title or "Why Us Item"

class ProductFAQ(Base):
    __tablename__ = "product_faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    sequence = Column(Integer, default=0, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="faqs")

    def __str__(self):
        return self.question

class ProductSocialTrust(Base):
    __tablename__ = "product_social_trusts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    name = Column(String, nullable=True) 
    
    logo_url = Column(String, nullable=False)     

    sequence = Column(Integer, default=0, index=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="social_trusts")

    def __str__(self):
        return self.name or "Partner Logo"