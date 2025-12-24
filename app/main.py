from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from app.routers.v1 import product as product_v1
from app.routers.v1 import blog as blog_v1
from app.routers.v1 import solution as solution_v1
from app.routers.v1 import social_trust as social_trust_v1
from app.routers.v1 import service as service_v1
from app.routers.v1 import promo as promo_v1
from app.routers.v1 import cron    
from app.db.session import engine, SessionLocal
from app.core.config import settings
import time
from sqlalchemy import func
from app.models.solutions import Solution
from app.models.service import ServicePage
from app.models.product import Product
from app.models.blog import Article, Author
from app.core.admin import (
    authentication_backend,
    UserAdmin,
    ProductAdmin, ProductFeatureAdmin, ProductWhyUsAdmin, ProductFAQAdmin, ProductSocialTrustLinkAdmin,
    SolutionAdmin, SolutionFeatureAdmin, SolutionWhyUsAdmin, SolutionFAQAdmin, SolutionRelatedProductAdmin, SolutionSocialTrustLinkAdmin,
    ArticleAdmin, AuthorAdmin, CategoryAdmin,
    SocialTrustAdmin,
    ServicePageAdmin, ServiceFocusItemAdmin, ServiceQuickStepAdmin, ServiceOfferingAdmin, ServiceMethodologyAdmin, ServiceCompetencyAdmin,
    PromoAdmin
)

tags_metadata = [
    {
        "name": "General",
        "description": "Health check and root connectivity endpoints.",
    },
    {
        "name": "Products",
        "description": "Endpoints to fetch product details.",
    },
    {
        "name": "Blogs",
        "description": "Endpoints for retrieving news, articles, authors, and categories.",
    },
    {
        "name": "Services",
        "description": "Endpoints for fetching Service landing pages.",
    },
    {
        "name": "Solutions",
        "description": "Endpoints for fetching Solution pages.",
    },
    {
        "name": "Social Trust",
        "description": "Endpoints for fetching global partner logos.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Solvera Corporate Website",
    version="1.0.0",
    openapi_tags=tags_metadata
)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://corporate-website-solvera-9wek.vercel.app",
    "https://corporate-website-solvera.vercel.app"
]

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://corporate-website-solvera.*\.vercel\.app"
)

app.include_router(promo_v1.router, prefix=settings.API_V1_PREFIX) 
app.include_router(product_v1.router, prefix=settings.API_V1_PREFIX, tags=["Products"])
app.include_router(blog_v1.router, prefix=settings.API_V1_PREFIX, tags=["Blogs"])
app.include_router(social_trust_v1.router, prefix=settings.API_V1_PREFIX, tags=["Social Trust"])
app.include_router(service_v1.router, prefix=settings.API_V1_PREFIX, tags=["Services"])
app.include_router(solution_v1.router, prefix=settings.API_V1_PREFIX, tags=["Solutions"]) 
app.include_router(cron.router, prefix="/api/cron", tags=["Cron Jobs"])

admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(ProductAdmin)
admin.add_view(ProductFeatureAdmin)
admin.add_view(ProductWhyUsAdmin)
admin.add_view(ProductFAQAdmin)

admin.add_view(SocialTrustAdmin)
admin.add_view(ProductSocialTrustLinkAdmin)

admin.add_view(SolutionAdmin)
admin.add_view(SolutionFeatureAdmin)
admin.add_view(SolutionWhyUsAdmin)
admin.add_view(SolutionFAQAdmin)
admin.add_view(SolutionRelatedProductAdmin)
admin.add_view(SolutionSocialTrustLinkAdmin)

admin.add_view(ServicePageAdmin)
admin.add_view(ServiceFocusItemAdmin)
admin.add_view(ServiceQuickStepAdmin)
admin.add_view(ServiceOfferingAdmin)
admin.add_view(ServiceMethodologyAdmin)
admin.add_view(ServiceCompetencyAdmin)
admin.add_view(PromoAdmin)

admin.add_view(ArticleAdmin)
admin.add_view(AuthorAdmin)
admin.add_view(CategoryAdmin)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": exc.errors()
            }
        },
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {}
            }
        },
    )

@app.get("/api/admin/stats", tags=["General"])
async def get_admin_stats(request: Request):
    db = SessionLocal()
    start_time = time.time()
    try:
        role = request.session.get("role")
        user_id = request.session.get("user_id")

        if role == "admin":
            articles_count = db.query(func.count(Article.id)).scalar()
            products_count = db.query(func.count(Product.id)).scalar()
            solutions_count = db.query(func.count(Solution.id)).scalar()
            services_count = db.query(func.count(ServicePage.id)).scalar()
            
            latency = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "role": "admin",
                "articles": articles_count,
                "products": products_count,
                "solutions": solutions_count,
                "services": services_count,
                "db_health": {
                    "status": "Healthy",
                    "latency_ms": round(latency, 2),
                    "last_check": time.time()
                }
            }
        elif role == "editor":
            author = db.query(Author).filter(Author.user_id == user_id).first()
            articles_data = []
            if author:
                articles = db.query(Article).filter(Article.publisher_id == author.id).order_by(Article.created_at.desc()).limit(10).all()
                for art in articles:
                    articles_data.append({
                        "id": str(art.id),
                        "title": art.title,
                        "published_at": art.published_at.isoformat() if art.published_at else None,
                        "created_at": art.created_at.isoformat()
                    })
            
            return {
                "success": True,
                "role": "editor",
                "articles": articles_data
            }
        
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(e)}
        )
    finally:
        db.close()

@app.get("/", tags=["General"])
async def root():
    return {"status": "ok", "message": "Solvera Backend is running"}