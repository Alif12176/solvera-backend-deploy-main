from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from sqlalchemy import func, or_

def get_product_list(
    db: Session, 
    page: int, 
    limit: int, 
    category: str = None, 
    search: str = None
):
    offset = (page - 1) * limit
    query = db.query(Product)

    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.hero_title.ilike(search_term),
                Product.hero_subtitle.ilike(search_term),
                Product.slug.ilike(search_term)
            )
        )

    total_items = query.count()
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()
    
    return products, total_items

def get_product_by_slug(db: Session, slug: str):
    product = db.query(Product).options(
        joinedload(Product.features),
        joinedload(Product.why_us),
        joinedload(Product.faqs)
    ).filter(Product.slug == slug).first()

    return product