from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class ServicePage(Base):
    __tablename__ = "service_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    slug = Column(String, unique=True, index=True) 
    page_name = Column(Text, nullable=False)
    
    hero_heading = Column(Text, nullable=False)
    hero_tagline = Column(Text, nullable=True)
    hero_bg_image = Column(String, nullable=True)

    focus_section_tagline = Column(Text, nullable=True)
    focus_section_heading = Column(Text, nullable=True)
    focus_section_desc = Column(Text, nullable=True)

    quick_step_layout = Column(String, default='steps', nullable=False)
    quick_step_heading = Column(Text, nullable=True)
    quick_step_subheading = Column(Text, nullable=True)
    quick_step_footer = Column(Text, nullable=True)

    offering_heading = Column(Text, nullable=True)
    offering_desc = Column(Text, nullable=True)

    methodology_layout = Column(String, default='timeline', nullable=False)
    methodology_footer = Column(Text, nullable=True)
    methodology_heading = Column(Text, nullable=True)
    methodology_desc = Column(Text, nullable=True)

    competency_footer = Column(Text, nullable=True)
    competency_heading = Column(Text, nullable=True)
    competency_desc = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    focus_items = relationship("ServiceFocusItem", back_populates="service_page", order_by="ServiceFocusItem.display_order", cascade="all, delete-orphan")
    quick_steps = relationship("ServiceQuickStep", back_populates="service_page", order_by="ServiceQuickStep.step_order", cascade="all, delete-orphan")
    
    offerings = relationship("ServiceOffering", back_populates="service_page", order_by="ServiceOffering.display_order", cascade="all, delete-orphan")
    
    methodologies = relationship("ServiceMethodology", back_populates="service_page", order_by="ServiceMethodology.phase_order", cascade="all, delete-orphan")
    competencies = relationship("ServiceCompetency", back_populates="service_page", order_by="ServiceCompetency.rank_order", cascade="all, delete-orphan")

    def __str__(self):
        return self.page_name

class ServiceFocusItem(Base):
    __tablename__ = "service_focus_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_page_id = Column(UUID(as_uuid=True), ForeignKey("service_pages.id"))
    card_title = Column(Text, nullable=False)
    card_desc = Column(Text, nullable=True)
    icon_image = Column(String, nullable=True)
    display_order = Column(Integer, default=0, index=True)
    service_page = relationship("ServicePage", back_populates="focus_items")

    def __str__(self):
        return self.card_title

class ServiceQuickStep(Base):
    __tablename__ = "service_quick_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_page_id = Column(UUID(as_uuid=True), ForeignKey("service_pages.id"))
    
    step_label = Column(String, nullable=True) 
    step_title = Column(Text, nullable=False)
    step_desc = Column(Text, nullable=True)
    
    checklist = Column(JSON, nullable=True) 
    
    step_order = Column(Integer, default=0, index=True)
    
    service_page = relationship("ServicePage", back_populates="quick_steps")

    def __str__(self):
        return self.step_title

class ServiceMethodology(Base):
    __tablename__ = "service_methodologies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_page_id = Column(UUID(as_uuid=True), ForeignKey("service_pages.id"))
    
    phase_number = Column(String, nullable=True)
    phase_title = Column(Text, nullable=False)
    phase_desc = Column(Text, nullable=True)
    
    icon_image = Column(String, nullable=True) 
    
    phase_order = Column(Integer, default=0, index=True)
    
    service_page = relationship("ServicePage", back_populates="methodologies")

    def __str__(self):
        return self.phase_title

class ServiceCompetency(Base):
    __tablename__ = "service_competencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_page_id = Column(UUID(as_uuid=True), ForeignKey("service_pages.id"))
    
    skill_name = Column(String, nullable=False)
    percentage_value = Column(Integer, nullable=False)
    
    rank_order = Column(Integer, default=0, index=True)
    
    service_page = relationship("ServicePage", back_populates="competencies")

    def __str__(self):
        return self.skill_name

class ServiceOffering(Base):
    __tablename__ = "service_offerings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    service_page_id = Column(UUID(as_uuid=True), ForeignKey("service_pages.id"))
    
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    checklist = Column(JSON, nullable=True) 
    
    icon_image = Column(String, nullable=True)
    highlight_badge = Column(String, nullable=True)
    
    button_text = Column(String, nullable=True)
    button_url = Column(String, nullable=True)
    
    display_order = Column(Integer, default=0, index=True)
    
    service_page = relationship("ServicePage", back_populates="offerings")

    def __str__(self):
        return self.title