from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer, Table, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="editor") 
    is_active = Column(Boolean, default=True)
    
    author_profile = relationship("Author", back_populates="user", uselist=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

article_categories = Table(
    'article_categories',
    Base.metadata,
    Column('article_id', UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, unique=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    articles = relationship("Article", back_populates="publisher")
    user = relationship("User", back_populates="author_profile")

    def __str__(self):
        return self.name

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    articles = relationship("Article", secondary=article_categories, back_populates="categories")

    def __str__(self):
        return self.name

class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    publisher_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True) 
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    publisher = relationship("Author", back_populates="articles")
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    
    def __str__(self):
        return self.title