from sqlalchemy.orm import Session, joinedload
from app.models.service import ServicePage

def get_all_services(db: Session):
    return db.query(ServicePage).order_by(ServicePage.updated_at.desc()).all()

def get_service_by_slug(db: Session, slug: str):
    service = db.query(ServicePage).options(
        joinedload(ServicePage.focus_items),
        joinedload(ServicePage.quick_steps),
        joinedload(ServicePage.methodologies),
        joinedload(ServicePage.competencies)
    ).filter(ServicePage.slug == slug).first()

    return service