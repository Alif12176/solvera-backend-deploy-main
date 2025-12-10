from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.blog_service import get_article_by_slug, get_latest_articles, get_all_categories
from app.schemas.v1.blog_schema import ArticleSchema, PaginatedArticleResponse, CategoryListResponse
from app.schemas.common import APIResponse
from typing import Optional

router = APIRouter()

@router.get(
    "/categories",
    response_model=APIResponse[CategoryListResponse],
    summary="Get List of Categories (Topics)",
)
def get_categories_list(db: Session = Depends(get_db)):
    categories = get_all_categories(db)
    data = CategoryListResponse(items=categories, count=len(categories))
    return APIResponse(success=True, data=data, error=None)

@router.get(
    "/articles", 
    response_model=APIResponse[PaginatedArticleResponse],
    summary="Get List of Articles",
)
def get_articles_list(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=50),
    category: Optional[str] = Query(None, description="Filter by category Name (e.g., 'Saham')"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    articles = get_latest_articles(db, limit=limit + 1, offset=offset, category_name=category)

    has_more = False
    if len(articles) > limit:
        has_more = True
        articles = articles[:limit]

    data = PaginatedArticleResponse(
        items=articles,
        page=page,
        limit=limit,
        has_more=has_more
    )
    
    return APIResponse(success=True, data=data, error=None)

@router.get(
    "/articles/{slug}", 
    response_model=APIResponse[ArticleSchema],
    summary="Get Article Detail",
)
def get_article_detail(
    slug: str, 
    db: Session = Depends(get_db)
):
    article = get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return APIResponse(success=True, data=article, error=None)