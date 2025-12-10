from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.blog import Article, Category
from typing import List, Optional, Tuple

def get_article_by_slug(db: Session, slug: str) -> Optional[Article]:
    return db.query(Article).options(
        joinedload(Article.publisher), 
        joinedload(Article.categories) 
    ).filter(Article.slug == slug).first()

def get_articles(
    db: Session, 
    limit: int = 10, 
    offset: int = 0, 
    category_slug: Optional[str] = None
) -> Tuple[List[Article], int]:
    query = db.query(Article).options(
        joinedload(Article.publisher),
        joinedload(Article.categories)
    ).filter(
        Article.published_at.isnot(None)
    )

    if category_slug:
        query = query.join(Article.categories).filter(Category.slug == category_slug)

    total = query.count()

    articles = query.order_by(
        Article.published_at.desc()
    ).offset(offset).limit(limit).all()

    return articles, total

def get_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.name.asc()).all()