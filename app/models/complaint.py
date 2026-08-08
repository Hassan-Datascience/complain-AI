from typing import Optional
from datetime import datetime

class Complaint:
    def __init__(
        self,
        complaint_id: str,
        description: str,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        location: Optional[str] = None,
        date: Optional[str] = None,
        status: str = "Open",
        assigned_department: Optional[str] = None,
        ai_summary: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        resolved_at: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.complaint_id = complaint_id
        self.description = description
        self.category = category
        self.priority = priority
        self.location = location
        self.date = date or datetime.utcnow().isoformat()
        self.status = status
        self.assigned_department = assigned_department
        self.ai_summary = ai_summary
        self.ai_confidence = ai_confidence
        self.resolved_at = resolved_at
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "complaint_id": self.complaint_id,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "location": self.location,
            "date": self.date,
            "status": self.status,
            "assigned_department": self.assigned_department,
            "ai_summary": self.ai_summary,
            "ai_confidence": self.ai_confidence,
            "resolved_at": self.resolved_at,
            "created_at": self.created_at,
        }
