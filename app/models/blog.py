from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

# 1. Tabel Authors
class Author(Base):
    __tablename__ = "authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    articles = relationship("Article", back_populates="author")

# 2. Tabel Categories
class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False, unique=True) # Contoh: "Berita", "Tutorial"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    articles = relationship("Article", back_populates="category")

# 3. Tabel Articles
class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    # Content
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)   
    content = Column(Text, nullable=False)     
    image = Column(String, nullable=True)    

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relasi Balik
    author = relationship("Author", back_populates="articles")
    category = relationship("Category", back_populates="articles")