from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.projects import router as projects_router
from app.api.contacts import router as contacts_router
from app.api.notifications import router as notifications_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(projects_router)
api_router.include_router(contacts_router)
api_router.include_router(notifications_router)
api_router.include_router(dashboard_router)
