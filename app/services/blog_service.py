from sqlalchemy.orm import Session, joinedload
from app.models.blog import Article
from typing import List, Optional

def get_article_by_slug(db: Session, slug: str) -> Optional[Article]:
    """
    Fetch a single article by slug.
    """
    article = db.query(Article).options(
        joinedload(Article.publisher), 
        joinedload(Article.categories) 
    ).filter(Article.slug == slug).first()

    return article

def get_latest_articles(db: Session, limit: int = 10, offset: int = 0) -> List[Article]:
    """
    Fetch a list of latest published articles with pagination.
    """
    articles = db.query(Article).options(
        joinedload(Article.publisher),
        joinedload(Article.categories)
    ).filter(
        Article.published_at.isnot(None)
    ).order_by(
        Article.published_at.desc()    
    ).offset(offset).limit(limit).all()

    return articles