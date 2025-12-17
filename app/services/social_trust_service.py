from sqlalchemy.orm import Session
from app.models.social_trust import SocialTrust

def get_all_social_trusts(db: Session):
    return db.query(SocialTrust).order_by(SocialTrust.sequence.asc()).all()