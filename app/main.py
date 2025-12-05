
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers.v1 import product as product_v1

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Solvera Backend is running"}

app.include_router(product_v1.router, prefix="/api/v1")

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
