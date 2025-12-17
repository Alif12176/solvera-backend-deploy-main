from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, func, Integer
from app.db.base import Base

class SocialTrust(Base):
    __tablename__ = "social_trusts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=False)
    sequence = Column(Integer, default=0, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __str__(self):
        return self.name