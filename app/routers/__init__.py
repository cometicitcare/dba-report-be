"""
Buddhist Affairs MIS Dashboard - Routers Package
"""
from app.routers.auth import router as auth_router, require_auth
from app.routers.dashboard import router as dashboard_router
from app.routers.section1 import router as section1_router
from app.routers.section2 import router as section2_router
from app.routers.section3 import router as section3_router
from app.routers.temples import router as temples_router
from app.routers.lookups import router as lookups_router
from app.routers.persons import router as persons_router

__all__ = [
    "auth_router",
    "require_auth",
    "dashboard_router",
    "section1_router",
    "section2_router",
    "section3_router",
    "temples_router",
    "lookups_router",
    "persons_router",
]

