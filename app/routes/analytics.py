from typing import Dict, Any
from fastapi import APIRouter
from app.schemas import AnalyticsSummaryResponse, AdvancedStatsResponse
from app.services.database_manager import DatabaseManager
from app.services.stats_service import StatsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Statistics"])

db = DatabaseManager()

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary():
    """
    Returns counts and distributions for categories, priorities, and statuses.
    """
    complaints = db.get_all_for_stats()
    stats = StatsService(complaints)
    
    return {
        "total_complaints": len(complaints),
        "categories": stats.get_category_distribution(),
        "priorities": stats.get_priority_distribution(),
        "statuses": stats.get_status_distribution(),
    }

@router.get("/stats", response_model=AdvancedStatsResponse)
def get_advanced_resolution_stats():
    """
    Exposes full statistical analysis on complaint resolution times:
    Mean, Median, Mode, Variance, Std Dev, Quartiles (Q1, Q3), IQR, Outlier threshold, and Narrative.
    """
    complaints = db.get_all_for_stats()
    stats = StatsService(complaints)
    return stats.get_resolution_stats()

@router.get("/trends")
def get_complaint_trends() -> Dict[str, Any]:
    """
    Exposes volume trends over time (daily counts).
    """
    complaints = db.get_all_for_stats()
    stats = StatsService(complaints)
    return stats.get_trends()
