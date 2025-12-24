from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from app.models.solutions import Solution, SolutionRelatedProduct, SolutionSocialTrustLink
from app.schemas.v1.solusi_schema import (
    Solution as SolutionSchema, 
    CoreBenefit, CoreValue, IndustrySection, IndustryItem, 
    CoreSolution, CoreSolutionItem, FAQItem, SocialTrustItem
)

def _map_to_schema(solution_db: Solution) -> SolutionSchema:
    core_benefits_list = []
    sorted_features = sorted(solution_db.features, key=lambda x: x.sequence or 0)
    for i, f in enumerate(sorted_features):
        s_title = solution_db.core_benefits_title if i == 0 else None
        s_subtitle = solution_db.core_benefits_subtitle if i == 0 else None
        
        core_benefits_list.append(
            CoreBenefit(
                id=f.id,
                section_title=s_title, 
                section_subtitle=s_subtitle,
                tab_label=f.tab_label,
                content_title=f.content_title,
                content_description=f.content_description,
                values=f.benefits or [],
                sequence=f.sequence
            )
        )
    
    core_values_list = [
        CoreValue(
            id=w.id,
            section_title=w.title,
            section_subtitle=w.description,
            icon=w.icon,
            icon_title=w.title,
            icon_description=w.description,
            sequence=w.sequence
        ) for w in solution_db.why_us if w.section_type == "fitur_inti"
    ]

    core_sol_items_db = [w for w in solution_db.why_us if w.section_type == "keunggulan_solusi"]
    
    core_sol_items = [
        CoreSolutionItem(
            id=w.id,
            icon=w.icon,
            title=w.title,
            description=w.description,
            sequence=w.sequence
        ) for w in core_sol_items_db
    ]
    
    core_solution_obj = None
    if core_sol_items:
        core_solution_obj = CoreSolution(
            section_title=solution_db.core_solution_title or "Keunggulan Solusi",
            section_subtitle=solution_db.core_solution_subtitle,
            items=core_sol_items
        )

    industry_items = []
    for rp in solution_db.related_products:
        if rp.product: 
            industry_items.append(IndustryItem(
                id=rp.product.id,
                slug=rp.product.slug,
                name=rp.product.name,
                icon=rp.icon_url, 
                description=rp.product.hero_subtitle,
                sequence=rp.sequence
            ))
            
    industry_section_obj = None
    if industry_items:
        industry_section_obj = IndustrySection(
            section_title="Industri Terkait",
            section_subtitle=None,
            industries=industry_items
        )

    faq_list = [
        FAQItem(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            sequence=faq.sequence
        ) for faq in solution_db.faqs
    ]

    trusted_list = []
    if solution_db.trusted_by:
        sorted_links = sorted(solution_db.trusted_by, key=lambda x: x.sequence or 0)
        for link in sorted_links:
            if link.partner:
                trusted_list.append(SocialTrustItem(
                    id=link.partner.id,
                    name=link.partner.name,
                    logo_url=link.partner.logo_url,
                    sequence=link.sequence
                ))

    return SolutionSchema(
        id=solution_db.id,
        slug=solution_db.slug,
        name=solution_db.name,
        category=solution_db.category,
        hero_title=solution_db.hero_title,
        hero_subtitle=solution_db.hero_subtitle,
        hero_image=solution_db.hero_image,
        cta_primary_text=solution_db.cta_primary_text,
        cta_secondary_text=solution_db.cta_secondary_text,
        cta_image=solution_db.cta_image,
        core_benefits=core_benefits_list,
        core_values=core_values_list,
        industry_section=industry_section_obj,
        core_solution=core_solution_obj,
        faqs=faq_list,
        trusted_by=trusted_list,
        created_at=solution_db.created_at,
        updated_at=solution_db.updated_at
    )

def get_solution_by_slug(db: Session, slug: str) -> Optional[SolutionSchema]:
    solution_db = db.query(Solution).options(
        joinedload(Solution.features),
        joinedload(Solution.why_us),
        joinedload(Solution.faqs),
        joinedload(Solution.related_products).joinedload(SolutionRelatedProduct.product),
        joinedload(Solution.trusted_by).joinedload(SolutionSocialTrustLink.partner)
    ).filter(Solution.slug == slug).first()

    if not solution_db:
        return None

    return _map_to_schema(solution_db)

def get_all_solutions(db: Session, page: int = 1, page_size: int = 10, search: str = None) -> List[SolutionSchema]:
    skip = (page - 1) * page_size

    query = db.query(Solution).options(
        joinedload(Solution.features),
        joinedload(Solution.why_us),
        joinedload(Solution.faqs),
        joinedload(Solution.related_products).joinedload(SolutionRelatedProduct.product),
        joinedload(Solution.trusted_by).joinedload(SolutionSocialTrustLink.partner)
    )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Solution.name.ilike(search_filter),
                Solution.hero_title.ilike(search_filter),
                Solution.category.ilike(search_filter)
            )
        )

    solutions_db = query.order_by(Solution.updated_at.desc()) \
                        .offset(skip) \
                        .limit(page_size) \
                        .all()

    return [_map_to_schema(s) for s in solutions_db]