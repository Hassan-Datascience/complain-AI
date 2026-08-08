from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas import ComplaintCreate, ComplaintResponse
from app.services.complaint_manager import ComplaintManager

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Shared service instance
manager = ComplaintManager()

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate):
    """
    Submits a new citizen complaint.
    Triggers AI classification, priority prediction, LLM summarization,
    and automatic department assignment.
    """
    try:
        result = manager.submit_complaint(
            description=payload.description,
            location=payload.location,
            date=payload.date
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your complaint: {str(e)}"
        )

@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    department: Optional[str] = Query(None, description="Filter by assigned department"),
    date_from: Optional[str] = Query(None, description="ISO start date filter"),
    date_to: Optional[str] = Query(None, description="ISO end date filter"),
):
    """
    Retrieves all complaints with optional filtering by category, priority, status,
    location, department, or date range. Unknown filters are gracefully ignored.
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
    # Clean out None values
    active_filters = {k: v for k, v in filters.items() if v is not None}
    return manager.list_complaints(active_filters)

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str):
    """
    Retrieves a single complaint by its unique ID (e.g. CMP-A1B2C3D4).
    """
    complaint = manager.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID '{complaint_id}' was not found."
        )
    return complaint
