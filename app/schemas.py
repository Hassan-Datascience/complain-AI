from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class ComplaintCreate(BaseModel):
    description: str = Field(..., min_length=10, description="Detailed complaint description (minimum 10 characters)")
    location: Optional[str] = Field(None, description="Physical location or landmark")
    date: Optional[str] = Field(None, description="ISO timestamp format date")

class ComplaintResponse(BaseModel):
    complaint_id: str
    description: str
    category: Optional[str] = None
    priority: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    status: str
    assigned_department: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_summary_fallback: Optional[bool] = False
    submitted_by: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str = Field(..., description="Target complaint status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Open", "Assigned", "In Progress", "Resolved"}
        if v not in allowed:
            raise ValueError(f"Invalid status '{v}'. Allowed values are: {', '.join(allowed)}")
        return v

class DepartmentAssign(BaseModel):
    department: str = Field(..., min_length=2, description="Name of the department to assign")

class AnalyticsSummaryResponse(BaseModel):
    total_complaints: int
    categories: Dict[str, int]
    priorities: Dict[str, int]
    statuses: Dict[str, int]

class AdvancedStatsResponse(BaseModel):
    total_resolved: int
    mean_hours: float
    median_hours: float
    mode_hours: float
    min_hours: float
    max_hours: float
    range_hours: float
    variance_hours: float
    std_dev_hours: float
    q1_hours: float
    q3_hours: float
    iqr_hours: float
    outlier_threshold_hours: float
    outliers_count: int
    interpretation: str
