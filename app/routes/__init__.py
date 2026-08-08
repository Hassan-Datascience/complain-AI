from app.routes.complaints import router as complaints_router
from app.routes.admin import router as admin_router
from app.routes.analytics import router as analytics_router

__all__ = ["complaints_router", "admin_router", "analytics_router"]
