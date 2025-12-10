from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.blog_service import get_article_by_slug, get_articles, get_categories
from app.schemas.v1.blog_schema import ArticleSchema, ArticleListResponse, CategoryItem
from app.schemas.common import APIResponse
from typing import List, Optional

router = APIRouter()

@router.get(
    "/articles", 
    response_model=APIResponse[ArticleListResponse],
    summary="Get List of Articles",
    description="Retrieve paginated articles. Can be filtered by category slug."
)
def list_articles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category slug (e.g., 'saham')"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    items, total = get_articles(db, limit=limit, offset=offset, category_slug=category)
    
    data = ArticleListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )
    return APIResponse(success=True, data=data, error=None)

@router.get(
    "/articles/{slug}", 
    response_model=APIResponse[ArticleSchema],
    summary="Get Article Detail",
    description="Retrieve full details of a single article by its slug."
)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return APIResponse(success=True, data=article, error=None)

@router.get(
    "/categories",
    response_model=APIResponse[List[CategoryItem]],
    summary="Get All Categories",
    description="Retrieve a list of all available blog categories/topics."
)
def list_categories(db: Session = Depends(get_db)):
    categories = get_categories(db)
    return APIResponse(success=True, data=categories, error=None)