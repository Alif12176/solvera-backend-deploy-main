from pydantic import BaseModel, Field, model_serializer
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True 

# --- Child Schemas (Required so Pydantic can extract data from ORM) ---

class ServiceFocusItemSchema(ORMBase):
    id: UUID
    card_title: str
    card_desc: Optional[str] = None
    icon_image: Optional[str] = None
    display_order: Optional[int] = 0

class ServiceQuickStepSchema(ORMBase):
    id: UUID
    step_label: Optional[str] = None
    step_title: str
    step_desc: Optional[str] = None
    checklist: Optional[List[str]] = None 
    step_order: Optional[int] = 0

class ServiceOfferingSchema(ORMBase):
    id: UUID
    title: str
    description: Optional[str] = None
    checklist: Optional[List[str]] = None
    icon_image: Optional[str] = None
    highlight_badge: Optional[str] = None
    button_text: Optional[str] = None
    button_url: Optional[str] = None
    display_order: Optional[int] = 0

class ServiceMethodologySchema(ORMBase):
    id: UUID
    phase_number: Optional[str] = None
    phase_title: str
    phase_desc: Optional[str] = None
    icon_image: Optional[str] = None
    phase_order: Optional[int] = 0

class ServiceCompetencySchema(ORMBase):
    id: UUID
    skill_name: str
    percentage_value: int
    rank_order: Optional[int] = 0

# --- Main Schema ---

class ServicePageSchema(ORMBase):
    id: UUID 
    slug: str
    page_name: str
    
    hero_heading: str
    hero_tagline: Optional[str] = None
    hero_bg_image: Optional[str] = None
    
    # Focus Section Fields
    focus_section_tagline: Optional[str] = None
    focus_section_heading: Optional[str] = None
    focus_section_desc: Optional[str] = None
    focus_items: List[ServiceFocusItemSchema] = []

    # Quick Steps Fields
    quick_step_layout: str = 'steps'
    quick_step_heading: Optional[str] = None
    quick_step_subheading: Optional[str] = None
    quick_step_footer: Optional[str] = None
    quick_steps: List[ServiceQuickStepSchema] = []

    # Offerings Fields
    offering_heading: Optional[str] = None
    offering_desc: Optional[str] = None
    offerings: List[ServiceOfferingSchema] = []

    # Methodology Fields
    methodology_layout: str = 'timeline'
    methodology_footer: Optional[str] = None
    methodology_heading: Optional[str] = None
    methodology_desc: Optional[str] = None
    methodologies: List[ServiceMethodologySchema] = []

    # Competency Fields
    competency_footer: Optional[str] = None
    competency_heading: Optional[str] = None
    competency_desc: Optional[str] = None
    competencies: List[ServiceCompetencySchema] = []
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_serializer(mode='wrap')
    def dynamic_response_structure(self, handler) -> dict[str, Any]:
        # 1. Basic Data
        data = {
            "id": self.id,
            "slug": self.slug,
            "page_name": self.page_name,
            "hero": {
                "heading": self.hero_heading,
                "tagline": self.hero_tagline,
                "bg_image": self.hero_bg_image
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        # 2. Focus Section (Only add if items exist)
        if self.focus_items:
            data['focus_section'] = {
                "tagline": self.focus_section_tagline,
                "heading": self.focus_section_heading,
                "description": self.focus_section_desc,
                "items": [
                    {
                        "id": i.id,
                        "title": i.card_title,
                        "description": i.card_desc,
                        "icon": i.icon_image,
                        "order": i.display_order
                    } for i in sorted(self.focus_items, key=lambda x: x.display_order or 0)
                ]
            }

        # 3. Quick Steps / Standards Section
        if self.quick_steps:
            layout = self.quick_step_layout
            items_data = []
            
            # Sort by step_order
            sorted_steps = sorted(self.quick_steps, key=lambda x: x.step_order or 0)
            
            for s in sorted_steps:
                if layout == 'steps':
                    # Structure 1: Horizontal Steps (Page 1 & 3)
                    items_data.append({
                        "type": "step",
                        "id": s.id,
                        "label": s.step_label,
                        "title": s.step_title,
                        "description": s.step_desc
                    })
                elif layout == 'standards_grid':
                    # Structure 2: Checklist Cards (Page 2)
                    items_data.append({
                        "type": "standard_card",
                        "id": s.id,
                        "title": s.step_title,
                        "checklist": s.checklist or []
                    })

            data['quick_steps_section'] = {
                "layout": layout, # 'steps' or 'standards_grid'
                "heading": self.quick_step_heading,
                "subheading": self.quick_step_subheading,
                "footer": self.quick_step_footer,
                "items": items_data
            }

        # 4. Offerings Section (Only Page 3 has this)
        if self.offerings:
            data['offerings_section'] = {
                "heading": self.offering_heading,
                "description": self.offering_desc,
                "items": [
                    {
                        "id": o.id,
                        "title": o.title,
                        "description": o.description,
                        "checklist": o.checklist or [],
                        "icon": o.icon_image,
                        "badge": o.highlight_badge,
                        "button": {
                            "text": o.button_text,
                            "url": o.button_url
                        } if o.button_text else None
                    } for o in sorted(self.offerings, key=lambda x: x.display_order or 0)
                ]
            }

        # 5. Methodology Section
        if self.methodologies:
            layout = self.methodology_layout
            meth_data = []
            
            sorted_meth = sorted(self.methodologies, key=lambda x: x.phase_order or 0)
            
            for m in sorted_meth:
                base_item = {
                    "id": m.id,
                    "title": m.phase_title,
                    "description": m.phase_desc
                }
                
                if layout == 'timeline':
                    # Structure 1: Vertical Timeline (Page 1)
                    meth_data.append({
                        **base_item,
                        "type": "timeline_phase",
                        "number": m.phase_number
                    })
                elif layout == 'roles_grid':
                    # Structure 2: Icon Grid (Page 2 & 3)
                    meth_data.append({
                        **base_item,
                        "type": "role_card",
                        "icon": m.icon_image
                    })

            data['methodology_section'] = {
                "layout": layout, # 'timeline' or 'roles_grid'
                "heading": self.methodology_heading,
                "description": self.methodology_desc,
                "footer": self.methodology_footer,
                "items": meth_data
            }

        # 6. Competency Section
        if self.competencies:
            data['competency_section'] = {
                "heading": self.competency_heading,
                "description": self.competency_desc,
                "footer": self.competency_footer,
                "items": [
                    {
                        "id": c.id,
                        "name": c.skill_name,
                        "percentage": c.percentage_value
                    } for c in sorted(self.competencies, key=lambda x: x.rank_order or 0)
                ]
            }

        return data

class ServiceListResponse(BaseModel):
    items: List[ServicePageSchema]
    count: int