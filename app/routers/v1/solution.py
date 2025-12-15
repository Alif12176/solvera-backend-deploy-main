from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.common import APIResponse
from app.services import solution_service
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=APIResponse)
def get_all_solutions(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search solutions by name, category, or title"),
    db: Session = Depends(get_db)
):
    solutions = solution_service.get_all_solutions(
        db, 
        page=page, 
        page_size=page_size, 
        search=search
    )
    return APIResponse(success=True, data=solutions, error=None)

@router.get("/{slug}", response_model=APIResponse)
def get_solution_by_slug(slug: str, db: Session = Depends(get_db)):
    solution_data = solution_service.get_solution_by_slug(db, slug)
    
    if not solution_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution with slug '{slug}' not found"
        )

    return APIResponse(success=True, data=solution_data, error=None)