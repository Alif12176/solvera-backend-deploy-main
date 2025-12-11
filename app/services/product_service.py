from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from sqlalchemy import func

def get_all_products(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    query = db.query(Product)
    
    total_items = query.count()
    products = query.offset(offset).limit(limit).all()
    
    return products, total_items

def get_product_by_slug(db: Session, slug: str):
    product = db.query(Product).options(
        joinedload(Product.features),
        joinedload(Product.why_us),
        joinedload(Product.faqs)
    ).filter(Product.slug == slug).first()

    return product

def get_product_by_category(db: Session, category: str, page: int, limit: int):
    offset = (page - 1) * limit
    query = db.query(Product).filter(func.lower(Product.category) == category.lower())
    
    total_items = query.count()
    products = query.offset(offset).limit(limit).all()
    
    return products, total_items