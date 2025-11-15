from typing import Generator

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ....services import AuthService
from ....database import Database

database = Database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_auth_service() -> Generator[AuthService, None, None]:
    """
    Dependência para fornecer uma instância de AuthService com sessão do banco.
    """
    session = database.get_session()
    try:
        yield AuthService(session)
    finally:
        session.close()

class AuthController:
    router = APIRouter()

    @router.post(
        "/token",
        tags=["auth"],
        summary="Login de usuário",
        description="Autentica um usuário com email e senha. Retorna um token JWT se autenticado.",
        responses={
            200: {
                "description": "Login realizado com sucesso",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer"
                        }
                    }
                },
            },
            401: {
                "description": "Usuário ou senha inválidos",
                "content": {"application/json": {"example": {"detail": "Usuário ou senha inválidos"}}},
            },
            422: {"description": "Erro de validação de dados"}
        },
    )
    async def login(
        username: str = Form(..., description="Email do usuário"),
        password: str = Form(..., description="Senha do usuário"),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        token = auth_service.authenticate_user(username, password)
        return {"access_token": token, "token_type": "bearer"}

    @router.post("/refresh", tags=["auth"], summary="Atualiza o access token usando o refresh token")
    async def refresh_token(
        refresh_token: str = Form(...),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        token = auth_service.refresh_access_token(refresh_token)
        return {"access_token": token, "token_type": "bearer"}
