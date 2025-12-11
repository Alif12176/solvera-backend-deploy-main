from app.schemas.v1.solusi_schema import Solution, CoreBenefit, CoreValue, IndustrySection, IndustryItem, CoreSolution, CoreSolutionItem, FAQItem
from app.schemas.common import APIResponse
from uuid import uuid4
from datetime import datetime

def get_all_solutions_dummy():
    dummy_solutions = [
        Solution(
            id=uuid4(),
            slug="sales-management",
            name="Sales Management",
            category="sales",
            hero_title="Kelola Penjualan dengan Cepat, Akurat & Terintegrasi",
            hero_subtitle="Solusi Sales Management membantu tim sales bekerja lebih cepat, efisien, dan akurat.",
            core_benefits=[
                CoreBenefit(
                    id=uuid4(),
                    tab_label="Pipeline Terstruktur",
                    content_title="Kontrol pipeline lebih mudah",
                    sequence=1
                )
            ],
            core_values=[
                CoreValue(
                    id=uuid4(),
                    icon="speed",
                    icon_title="Efisien",
                    icon_description="Meningkatkan efisiensi tim sales",
                    sequence=1
                )
            ],
            industry_section=IndustrySection(
                section_title="Industri Terkait",
                industries=[
                    IndustryItem(
                        id=uuid4(),
                        name="Properti & Real Estate",
                        description="Lead-nya banyak, proses panjang.",
                        sequence=1
                    )
                ]
            ),
            core_solution=CoreSolution(
                section_title="Keunggulan Solusi Kami",
                section_subtitle="Kami bantu tim sales bekerja lebih cepat, efisien, dan akurat dari awal hingga closing.",
                items=[
                    CoreSolutionItem(
                        id=uuid4(),
                        icon="link",
                        title="Integrasi modul Finance, Inventory, dan CRM.",
                        description="Integrasi modul Finance, Inventory, dan CRM.",
                        sequence=1
                    )
                ]
            ),
            faqs=[
                FAQItem(
                    id=uuid4(),
                    question="Apakah sistem ini mendukung multi pipeline?",
                    answer="Ya, bisa untuk multi pipeline.",
                    sequence=1
                )
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    return APIResponse(success=True, data=dummy_solutions, error=None)