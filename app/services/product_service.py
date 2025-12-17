from sqlalchemy.orm import Session, joinedload
from app.models.product import Product, ProductSocialTrustLink
from sqlalchemy import func

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
        search_term_wildcard = f"%{search}%"
        
        search_expression = func.concat(
            func.coalesce(Product.name, ''), ' ', 
            func.coalesce(Product.hero_title, ''), ' ', 
            func.coalesce(Product.hero_subtitle, '')
        )
        query = query.filter(search_expression.ilike(search_term_wildcard))
        
        query = query.order_by(
            Product.name.op('<->')(search),
            Product.hero_title.op('<->')(search),
            Product.hero_subtitle.op('<->')(search)
        )
    else:
        query = query.order_by(Product.created_at.desc())

    total_items = query.count()
    products = query.offset(offset).limit(limit).all()
    
    return products, total_items

def get_product_by_slug(db: Session, slug: str):
    product = db.query(Product).options(
        joinedload(Product.features),
        joinedload(Product.why_us),
        joinedload(Product.faqs),
        joinedload(Product.trusted_by).joinedload(ProductSocialTrustLink.partner)
    ).filter(Product.slug == slug).first()

    return product