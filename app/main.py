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
from app.db.session import engine
from app.core.config import settings
from app.core.admin import (
    authentication_backend,
    UserAdmin,
    ProductAdmin, ProductFeatureAdmin, ProductWhyUsAdmin, ProductFAQAdmin, ProductSocialTrustLinkAdmin, SocialTrustAdmin,
    SolutionAdmin, SolutionFeatureAdmin, SolutionWhyUsAdmin, SolutionFAQAdmin, SolutionRelatedProductAdmin,
    ArticleAdmin, AuthorAdmin, CategoryAdmin
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
        "name": "Solutions",
        "description": "Endpoints for fetching Solution pages.",
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
     # 👇 Tambahkan domain Vercel Anda di sini:
    "https://corporate-website-solvera-9wek.vercel.app",  # Domain Preview yang sedang error
    "https://corporate-website-solvera.vercel.app"

]

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 👇 OPSI TAMBAHAN (untuk Vercel):
    # regex agar semua link preview Vercel otomatis diizinkan tanpa perlu add manual satu-satu
    allow_origin_regex="https://corporate-website-solvera.*\.vercel\.app"

)

app.include_router(product_v1.router, prefix=settings.API_V1_PREFIX, tags=["Products"])
app.include_router(blog_v1.router, prefix=settings.API_V1_PREFIX, tags=["Blogs"])
app.include_router(solution_v1.router, prefix=settings.API_V1_PREFIX, tags=["Solutions"])

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

@app.get("/", tags=["General"])
async def root():
    return {"status": "ok", "message": "Solvera Backend is running"}