from fastapi import APIRouter

from app.controllers.health_controller import router as health_router
from routes.project1 import router as project1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(project1_router)
