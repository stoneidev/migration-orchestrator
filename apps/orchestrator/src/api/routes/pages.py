from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.validators import validate_page_id
from src.db.deps import get_db
from src.db.models import Page

router = APIRouter()


@router.get("/pages")
def list_pages(db: Session = Depends(get_db)):
    pages = db.query(Page).all()
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "module": p.module,
                "title": p.title,
                "complexity": p.complexity,
                "migration_status": p.migration_status,
                "current_step": p.current_step,
                "total_cost": p.total_cost,
            }
            for p in pages
        ],
    }


@router.get("/pages/{page_id}")
def get_page(page_id: str, db: Session = Depends(get_db)):
    page_id = validate_page_id(page_id)
    page = db.get(Page, page_id)
    if page is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "PAGE-001", "message": f"Page '{page_id}' not found"},
            },
        )
    return {
        "success": True,
        "data": {
            "id": page.id,
            "module": page.module,
            "title": page.title,
            "complexity": page.complexity,
            "spec_status": page.spec_status,
            "spec_score": page.spec_score,
            "migration_status": page.migration_status,
            "current_step": page.current_step,
            "branch_name": page.branch_name,
            "total_cost": page.total_cost,
            "total_input_tokens": page.total_input_tokens,
            "total_output_tokens": page.total_output_tokens,
        },
    }
