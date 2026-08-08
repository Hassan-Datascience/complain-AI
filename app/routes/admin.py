from fastapi import APIRouter, HTTPException, status
from app.schemas import StatusUpdate, DepartmentAssign, ComplaintResponse
from app.services.complaint_manager import ComplaintManager

router = APIRouter(prefix="/complaints", tags=["Admin Operations"])

manager = ComplaintManager()

@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(complaint_id: str, payload: StatusUpdate):
    """
    Admin action: Updates complaint status (Open, Assigned, In Progress, Resolved).
    If status is set to 'Resolved', sets the resolution timestamp automatically.
    """
    success = manager.update_status(complaint_id, payload.status)
    if not success:
        existing = manager.get_complaint(complaint_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Complaint '{complaint_id}' not found."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition to '{payload.status}'."
        )
    return manager.get_complaint(complaint_id)

@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
def reassign_complaint_department(complaint_id: str, payload: DepartmentAssign):
    """
    Admin action: Manually overrides department assignment for a complaint.
    """
    success = manager.assign_department(complaint_id, payload.department)
    if not success:
        existing = manager.get_complaint(complaint_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Complaint '{complaint_id}' not found."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update department assignment."
        )
    return manager.get_complaint(complaint_id)
