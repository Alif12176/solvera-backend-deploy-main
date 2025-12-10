from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers.v1 import product as product_v1
from app.routers.v1 import blog as blog_v1 

tags_metadata = [
    {
        "name": "General",
        "description": "Health check and root connectivity endpoints.",
    },
    {
        "name": "Products & Solutions",
        "description": "Endpoints to fetch product details (ERP, CRM) and Solutions.",
    },
    {
        "name": "Blogs & Articles",
        "description": "Endpoints for retrieving news, articles, authors, and categories.",
    },
]

app = FastAPI(
    title="Solvera Corporate Website API",
    description="Backend API for Solvera Corporate Website (Next.js)",
    version="1.0.0",
    openapi_tags=tags_metadata
)

@app.get("/", tags=["General"])
async def root():
    return {"status": "ok", "message": "Solvera Backend is running"}

app.include_router(
    product_v1.router, 
    prefix="/api/v1", 
    tags=["Products & Solutions"]
)

app.include_router(
    blog_v1.router, 
    prefix="/api/v1", 
    tags=["Blogs & Articles"]
)

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