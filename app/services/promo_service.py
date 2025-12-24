from sqlalchemy.orm import Session
from app.models.promo import Promo
from app.schemas.v1.promo_schema import PromoCreate, PromoUpdate

def get_active_promo(db: Session):
    return db.query(Promo).filter(Promo.is_active == True).first()

def get_promo(db: Session, promo_id: str):
    return db.query(Promo).filter(Promo.id == promo_id).first()

def create_promo(db: Session, promo: PromoCreate):
    db_promo = Promo(**promo.model_dump())
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    return db_promo

def update_promo(db: Session, promo_id: str, promo_update: PromoUpdate):
    db_promo = get_promo(db, promo_id)
    if not db_promo:
        return None
    
    update_data = promo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_promo, key, value)
    
    db.commit()
    db.refresh(db_promo)
    return db_promo

def delete_promo(db: Session, promo_id: str):
    db_promo = get_promo(db, promo_id)
    if not db_promo:
        return False
    db.delete(db_promo)
    db.commit()
    return True
