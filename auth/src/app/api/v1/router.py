from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.google_ouath import router as google_oauth_router
from app.api.v1.routes.roles import router as roles_router
from app.api.v1.routes.session import router as session_router
from app.api.v1.routes.user_role import router as user_role_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router, prefix="/auth/jwt", tags=["Авторизация"])
router.include_router(roles_router, prefix="/roles", tags=["Роли"])
router.include_router(
    user_role_router, prefix="/user_role", tags=["Роли пользователей"]
)
router.include_router(session_router, prefix="/sessions", tags=["Сессии"])
router.include_router(
    google_oauth_router, prefix="/oauth/google", tags=["OAuth"]
)
