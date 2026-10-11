from .auth import router as auth_router
from .students import router as students_router
from .rooms import router as rooms_router
from .allocations import router as allocations_router
from .complaints import router as complaints_router
from .visitors import router as visitors_router
from .notices import router as notices_router
from .feedback import router as feedback_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "students_router",
    "rooms_router",
    "allocations_router",
    "complaints_router",
    "visitors_router",
    "notices_router",
    "feedback_router",
    "analytics_router",
]
