from sqlalchemy.orm import Session, joinedload
from app.models.blog import Article

def get_article_by_slug(db: Session, slug: str):
    """
    Mengambil 1 artikel lengkap dengan data Author dan Category-nya.
    """
    article = db.query(Article).options(
        joinedload(Article.author),
        joinedload(Article.category)
    ).filter(Article.slug == slug).first()

    return article

def get_latest_articles(db: Session, limit: int = 5):
    """
    Mengambil list artikel terbaru untuk homepage/sidebar.
    """
    articles = db.query(Article).options(
        joinedload(Article.author),
        joinedload(Article.category)
    ).order_by(Article.created_at.desc()).limit(limit).all()

    return articles