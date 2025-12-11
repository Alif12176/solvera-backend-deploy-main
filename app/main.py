from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v1 import product as product_v1
from app.routers.v1 import blog as blog_v1

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
]

app = FastAPI(
    title="Solvera Corporate Website API",
    description="Backend API for Solvera Corporate Website",
    version="1.0.0",
    openapi_tags=tags_metadata
)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_v1.router, prefix="/api/v1", tags=["Products"])
app.include_router(blog_v1.router, prefix="/api/v1", tags=["Blogs"])

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