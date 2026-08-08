import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.services.database_manager import DatabaseManager
from app.services.ai_analyzer import AIAnalyzer

class ComplaintManager:
    """
    Business Logic Layer:
    Orchestrates Citizen complaint submission flow:
    Citizen Input -> ComplaintManager -> AIAnalyzer -> Auto Department Mapping -> DatabaseManager
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None, ai_analyzer: Optional[AIAnalyzer] = None):
        self.db = db_manager or DatabaseManager()
        self.ai = ai_analyzer or AIAnalyzer()

    def submit_complaint(
        self,
        description: str,
        location: Optional[str] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes new complaint:
        1. Generates unique ID
        2. Executes AI pipeline (category, priority, confidence, LLM summary)
        3. Maps category -> department
        4. Saves to SQLite database
        """
        complaint_id = f"CMP-{uuid.uuid4().hex[:8].upper()}"
        iso_date = date or datetime.utcnow().isoformat()

        # Run AI Analysis
        ai_output = self.ai.analyze(description)

        category = ai_output.get("category", "Other")
        priority = ai_output.get("priority", "Medium")
        ai_summary = ai_output.get("ai_summary")
        ai_confidence = ai_output.get("ai_confidence")

        # Auto-assign department based on AI category
        assigned_dept = self.db.get_department_for_category(category)
        if not assigned_dept:
            assigned_dept = "General Services Department"

        complaint_data = {
            "complaint_id": complaint_id,
            "description": description,
            "category": category,
            "priority": priority,
            "location": location,
            "date": iso_date,
            "status": "Open",
            "assigned_department": assigned_dept,
            "ai_summary": ai_summary,
            "ai_confidence": ai_confidence,
            "ai_summary_fallback": ai_output.get("ai_summary_fallback", False)
        }

        # Persist to database
        success = self.db.insert_complaint(complaint_data)
        if not success:
            raise RuntimeError("Database persistence error while inserting complaint.")

        return complaint_data

    def get_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_complaint(complaint_id)

    def list_complaints(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.db.list_complaints(filters)

    def update_status(self, complaint_id: str, status: str) -> bool:
        return self.db.update_status(complaint_id, status)

    def assign_department(self, complaint_id: str, department: str) -> bool:
        return self.db.assign_department(complaint_id, department)
