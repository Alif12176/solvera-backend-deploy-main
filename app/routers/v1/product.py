from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.product_service import get_product_by_slug, get_all_products, get_product_by_category
from app.schemas.v1.product_schema import ProductSchema
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/products", response_model=APIResponse[list[ProductSchema]])
def list_products(category: str = None, db: Session = Depends(get_db)):
    if category:
        products = get_product_by_category(db, category)
    else:
        products = get_all_products(db)
    return APIResponse(success=True, data=products, error=None)

@router.get("/products/{slug}", response_model=APIResponse[ProductSchema])
def read_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    return APIResponse(success=True, data=product, error=None)