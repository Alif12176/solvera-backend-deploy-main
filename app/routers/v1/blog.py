from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.blog_service import get_article_by_slug
from app.schemas.v1.blog_schema import ArticleSchema
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/articles/{slug}", response_model=APIResponse[ArticleSchema])
def get_article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return APIResponse(success=True, data=article, error=None)
