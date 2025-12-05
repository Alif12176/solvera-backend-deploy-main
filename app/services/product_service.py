from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from sqlalchemy import func

def get_all_products(db: Session):
    """
    Mengambil semua data Product.
    """
    products = db.query(Product).all()
    return products

def get_product_by_slug(db: Session, slug: str):
    """
    Mengambil data Product lengkap dengan Features, WhyUs, dan FAQs.
    """
    product = db.query(Product).options(
        joinedload(Product.features),
        joinedload(Product.why_us),
        joinedload(Product.faqs)
    ).filter(Product.slug == slug).first()

    return product

def get_product_by_category(db: Session, category: str):
    """
    Mengambil semua data Product berdasarkan category.
    """
    products = db.query(Product).filter(func.lower(Product.category) == category.lower()).all()
    return products