from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import promo_service
from app.schemas.v1.promo_schema import PromoOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=PromoOut)
def read_active_promo(db: Session = Depends(get_db)):
    db_promo = promo_service.get_active_promo(db)
    if db_promo is None:
        raise HTTPException(status_code=404, detail="No active promo found")
    return PromoOut.from_orm_model(db_promo)
