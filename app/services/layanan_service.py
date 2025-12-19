from sqlalchemy.orm import Session, joinedload
from app.models.service import Service, ServiceSocialTrustLink

def get_all_services(db: Session):
    return db.query(Service).order_by(Service.updated_at.desc()).all()

def get_service_by_slug(db: Session, slug: str):
    service = db.query(Service).options(
        joinedload(Service.features),
        joinedload(Service.processes),
        joinedload(Service.faqs),
        joinedload(Service.trusted_by).joinedload(ServiceSocialTrustLink.partner)
    ).filter(Service.slug == slug).first()

    return service