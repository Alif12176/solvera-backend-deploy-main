from sqlalchemy.orm import Session, joinedload
from app.models.blog import Article, Category
from typing import List, Optional

def get_article_by_slug(db: Session, slug: str) -> Optional[Article]:
    article = db.query(Article).options(
        joinedload(Article.publisher),
        joinedload(Article.categories)
    ).filter(Article.slug == slug).first()

    return article

def get_latest_articles(
    db: Session, 
    limit: int = 10, 
    offset: int = 0, 
    category_name: Optional[str] = None
) -> List[Article]:
    query = db.query(Article).options(
        joinedload(Article.publisher),
        joinedload(Article.categories)
    ).filter(
        Article.published_at.isnot(None)
    )

    if category_name:
        query = query.join(Article.categories).filter(Category.name == category_name)

    articles = query.order_by(
        Article.published_at.desc()
    ).offset(offset).limit(limit).all()

    return articles

def get_all_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.name.asc()).all()