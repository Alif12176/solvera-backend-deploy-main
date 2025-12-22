from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.service_service import get_service_by_slug, get_all_services
from app.schemas.v1.service_schema import ServicePageSchema, ServiceListResponse
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/services", response_model=APIResponse[ServiceListResponse])
def list_services(db: Session = Depends(get_db)):
    services = get_all_services(db)
    data = ServiceListResponse(items=services, count=len(services))
    return APIResponse(success=True, data=data, error=None)

@router.get("/services/{slug}", response_model=APIResponse[ServicePageSchema])
def read_service_by_slug(slug: str, db: Session = Depends(get_db)):
    service = get_service_by_slug(db, slug)
    if not service:
        raise HTTPException(status_code=404, detail="Service Page Not Found")
    return APIResponse(success=True, data=service, error=None)