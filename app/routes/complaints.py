from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from app.schemas import ComplaintCreate, ComplaintResponse
from app.services.complaint_manager import ComplaintManager
from app.routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Shared service instance
manager = ComplaintManager()


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submits a new citizen complaint (requires authenticated user).
    Triggers AI classification, priority prediction, LLM summarization,
    and automatic department assignment. Auto-attaches submitted_by = user_id.
    """
    try:
        result = manager.submit_complaint(
            description=payload.description,
            location=payload.location,
            date=payload.date,
            submitted_by=current_user["user_id"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your complaint: {str(e)}"
        )


@router.get("/my", response_model=List[ComplaintResponse])
def get_my_complaints(current_user: dict = Depends(get_current_user)):
    """
    Retrieves all complaints submitted by the logged-in user.
    """
    return manager.list_complaints_by_user(current_user["user_id"])


@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    department: Optional[str] = Query(None, description="Filter by assigned department"),
    date_from: Optional[str] = Query(None, description="ISO start date filter"),
    date_to: Optional[str] = Query(None, description="ISO end date filter"),
    admin_user: dict = Depends(require_admin)
):
    """
    Retrieves all complaints (Admin only).
    """
    filters = {
        "category": category,
        "priority": priority,
        "status": status_filter,
        "location": location,
        "department": department,
        "date_from": date_from,
        "date_to": date_to,
    }
    active_filters = {k: v for k, v in filters.items() if v is not None}
    return manager.list_complaints(active_filters)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves a single complaint by ID.
    Citizens can only view their own complaints unless role == 'admin'.
    """
    complaint = manager.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID '{complaint_id}' was not found."
        )

    # Ownership check for non-admin users
    if current_user["role"] != "admin" and complaint.get("submitted_by") != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own complaints."
        )

    return complaint

