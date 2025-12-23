from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.blog_service import get_article_by_slug, get_latest_articles, get_all_categories
from app.schemas.v1.blog_schema import ArticleSchema, PaginatedArticleResponse, CategoryListResponse
from app.schemas.common import APIResponse
import vercel_blob
from PIL import Image
import io
import uuid
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

@router.post(
    "/upload-image",
    summary="Upload image, compress to WebP, and store in Vercel Blob"
)
async def upload_blog_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image = Image.open(file.file)
        if image.mode in ("CMYK", "P"):
            image = image.convert("RGB")

        output_buffer = io.BytesIO()
        image.save(output_buffer, format="WEBP", quality=80, optimize=True)
        output_buffer.seek(0)

        original_name = file.filename.rsplit('.', 1)[0]
        filename = f"{original_name}-{uuid.uuid4().hex[:8]}.webp"

        blob = vercel_blob.put(
            filename, 
            output_buffer.read(), 
            options={'access': 'public', 'content_type': 'image/webp'}
        )

        return {"url": blob['url']}

    except Exception as e:
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")