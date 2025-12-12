from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.common import APIResponse
from app.services import solution_service
from app.db.session import get_db

router = APIRouter()

@router.get("/{slug}", response_model=APIResponse)
def get_solution_by_slug(slug: str, db: Session = Depends(get_db)):
    solution_data = solution_service.get_solution_by_slug(db, slug)
    
    if not solution_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution with slug '{slug}' not found"
        )

    return APIResponse(success=True, data=solution_data, error=None)