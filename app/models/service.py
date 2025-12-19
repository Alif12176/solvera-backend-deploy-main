from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.social_trust import SocialTrust

class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    slug = Column(String, unique=True, index=True) 
    name = Column(Text, nullable=False)
    
    hero_title = Column(Text, nullable=False)
    hero_subtitle = Column(Text, nullable=True)
    hero_image = Column(String, nullable=True)

    cta_primary_text = Column(String, nullable=True)
    cta_secondary_text = Column(String, nullable=True)
    cta_image = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    features = relationship("ServiceFeature", back_populates="service", order_by="ServiceFeature.sequence", cascade="all, delete-orphan")
    processes = relationship("ServiceProcess", back_populates="service", order_by="ServiceProcess.sequence", cascade="all, delete-orphan")
    faqs = relationship("ServiceFAQ", back_populates="service", order_by="ServiceFAQ.sequence", cascade="all, delete-orphan")
    trusted_by = relationship("ServiceSocialTrustLink", back_populates="service", order_by="ServiceSocialTrustLink.sequence", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class ServiceFeature(Base):
    __tablename__ = "service_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    
    section_type = Column(String, default="GENERAL", index=True)
    
    title = Column(Text, nullable=False)    
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    
    sequence = Column(Integer, default=0, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    service = relationship("Service", back_populates="features")

    def __str__(self):
        return self.title

class ServiceProcess(Base):
    __tablename__ = "service_processes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    
    step_number = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    sequence = Column(Integer, default=0, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    service = relationship("Service", back_populates="processes")

    def __str__(self):
        return f"{self.step_number} - {self.title}"

class ServiceFAQ(Base):
    __tablename__ = "service_faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    sequence = Column(Integer, default=0, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    service = relationship("Service", back_populates="faqs")

    def __str__(self):
        return self.question

class ServiceSocialTrustLink(Base):
    __tablename__ = "service_social_trust_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    social_trust_id = Column(UUID(as_uuid=True), ForeignKey("social_trusts.id"))
    
    sequence = Column(Integer, default=0, index=True)

    service = relationship("Service", back_populates="trusted_by")
    partner = relationship("app.models.social_trust.SocialTrust") 

    def __str__(self):
        return f"Service Partner Link"