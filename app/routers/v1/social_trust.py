from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.social_trust import SocialTrust
from app.schemas.v1.social_trust_schema import SocialTrustSection, SocialTrustItem
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/social-trust", response_model=APIResponse[SocialTrustSection])
def get_social_trust_list(db: Session = Depends(get_db)):
    partners = db.query(SocialTrust).order_by(SocialTrust.sequence.asc()).all()
    
    data = SocialTrustSection(
        section_title="Dipercaya oleh Perusahaan Terdepan di Indonesia",
        items=partners
    )
    
    return APIResponse(success=True, data=data, error=None)