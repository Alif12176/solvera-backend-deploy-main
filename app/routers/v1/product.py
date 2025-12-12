from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.product_service import get_product_by_slug, get_product_list
from app.schemas.v1.product_schema import ProductSchema, ProductListResponse
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/products", response_model=APIResponse[ProductListResponse])
def list_products(
    category: Optional[str] = None, 
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    products, total_items = get_product_list(
        db=db, 
        page=page, 
        limit=limit, 
        category=category, 
        search=search
    )
    
    total_pages = (total_items + limit - 1) // limit

    response_data = {
        "items": products,
        "meta": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages
        }
    }

    return APIResponse(success=True, data=response_data, error=None)

@router.get("/products/{slug}", response_model=APIResponse[ProductSchema])
def read_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    return APIResponse(success=True, data=product, error=None)