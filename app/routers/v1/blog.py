from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.blog_service import get_article_by_slug, get_latest_articles
from app.schemas.v1.blog_schema import ArticleSchema, PaginatedArticleResponse
from app.schemas.common import APIResponse

router = APIRouter()

@router.get(
    "/articles", 
    response_model=APIResponse[PaginatedArticleResponse],
    summary="Get List of Articles",
    description="Retrieve latest articles with pagination. Used for Blog Landing Page.",
    response_description="A list of articles with author and category details."
)
def get_articles_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    articles = get_latest_articles(db, limit=limit + 1, offset=offset)

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
    description="Retrieve full details of an article by its slug.",
    response_description="Single article object with full content."
)
def get_article_detail(
    slug: str, 
    db: Session = Depends(get_db)
):
    article = get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return APIResponse(success=True, data=article, error=None)