from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Solution(Base):
    __tablename__ = "solutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    slug = Column(String, unique=True, index=True) 
    name = Column(Text, nullable=False)
    category = Column(String, nullable=True) 
    
    hero_title = Column(Text, nullable=False)
    hero_subtitle = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    features = relationship("SolutionFeature", back_populates="solution", order_by="SolutionFeature.sequence", cascade="all, delete-orphan")
    why_us = relationship("SolutionWhyUs", back_populates="solution", order_by="SolutionWhyUs.sequence", cascade="all, delete-orphan")
    faqs = relationship("SolutionFAQ", back_populates="solution", order_by="SolutionFAQ.sequence", cascade="all, delete-orphan")
    related_products = relationship("SolutionRelatedProduct", back_populates="solution", order_by="SolutionRelatedProduct.sequence", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class SolutionFeature(Base):
    __tablename__ = "solution_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id"))
    
    tab_label = Column(String, nullable=True) 
    content_title = Column(String, nullable=True) 
    content_description = Column(Text, nullable=True)
    
    benefits = Column(JSON, nullable=True) 
    
    sequence = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    solution = relationship("Solution", back_populates="features")

    def __str__(self):
        return self.tab_label or self.content_title or "Solution Feature"

class SolutionWhyUs(Base):
    __tablename__ = "solution_why_us"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id"))
    
    section_type = Column(String, nullable=False, default="VALUE") 
    
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    
    sequence = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    solution = relationship("Solution", back_populates="why_us")

    def __str__(self):
        return self.title or "Why Us Item"

class SolutionRelatedProduct(Base):
    __tablename__ = "solution_related_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id"))
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    sequence = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    solution = relationship("Solution", back_populates="related_products")
    product = relationship("app.models.product.Product")

    def __str__(self):
        return f"Related Product Seq: {self.sequence}"

class SolutionFAQ(Base):
    __tablename__ = "solution_faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id"))
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    sequence = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    solution = relationship("Solution", back_populates="faqs")

    def __str__(self):
        return self.question