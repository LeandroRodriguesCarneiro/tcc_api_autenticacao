from fastapi import APIRouter, status

from .controllers.auth_controller import AuthController
from .controllers.user_controller import UserController

router = APIRouter()

auth_controller = AuthController()
user_controller = UserController()

router.include_router(
    AuthController.router,
    prefix='/Auth',
    tags=['V1', 'Auth']
    )
router.include_router(
    UserController.router,
    prefix='/User',
    tags=['V1', 'User']
    )

@router.get(
    '/health', 
    status_code=status.HTTP_200_OK,
    summary="Verificar se a API está online",
    description="Verificar se a API está online e operando",
    responses={
        200: {"description": "ok"}
    }
)
def health():
    return {"status": "ok"}