from typing import Generator

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ....services.auth_service import AuthService
from ....database.database import Database

from .auth_controller import oauth2_scheme, get_auth_service

class UserController:
    router = APIRouter()
    @router.post(
        "/register",
        tags=["User"],
        summary="Registrar novo usuário",
        description="Cria um novo usuário com email, senha e nome completo.",
        responses={
            201: {
                "description": "Usuário criado com sucesso",
                "content": {
                    "application/json": {"example": {"message": "Usuário registrado com sucesso"}}
                },
            },
            400: {
                "description": "Email já cadastrado",
                "content": {"application/json": {"example": {"detail": "Email já existe"}}},
            },
        },
    )
    async def register(
        email: str = Form(..., description="Email do novo usuário"),
        password: str = Form(..., description="Senha do novo usuário"),
        full_name: str = Form(..., description="Nome completo do usuário"),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        result = auth_service.add_user(email, password, full_name)
        return result

    @router.put(
        "/change-password",
        tags=["User"],
        summary="Alterar senha do usuário",
        description="Permite ao usuário alterar sua senha fornecendo a senha antiga e a nova.",
        responses={
            200: {"description": "Senha alterada com sucesso", "content": {"application/json": {"example": {"message": "Senha alterada com sucesso"}}}},
            401: {"description": "Senha antiga incorreta", "content": {"application/json": {"example": {"detail": "Senha antiga inválida"}}}},
        },
    )
    async def change_password(
        old_password: str = Form(..., description="Senha atual do usuário"),
        new_password: str = Form(..., description="Nova senha"),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        user = auth_service.get_user_from_token(token)
        email = user.email
        result = auth_service.change_password(email, old_password, new_password)
        return result

    @router.delete(
        "/delete-user",
        tags=["User"],
        summary="Deletar usuário",
        description="Deleta o usuário autenticado.",
        responses={
            200: {"description": "Usuário deletado com sucesso", "content": {"application/json": {"example": {"message": "Usuário deletado com sucesso"}}}},
            401: {"description": "Usuário não encontrado ou token inválido", "content": {"application/json": {"example": {"detail": "Usuário não encontrado"}}}},
        },
    )
    async def delete_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        user = auth_service.get_user_from_token(token)
        email = user.email
        result = auth_service.delete_user(email)
        return result

    @router.get(
        "/me",
        tags=["auth"],
        summary="Obter dados do usuário",
        description="Retorna os dados do usuário autenticado.",
        responses={
            200: {
                "description": "Dados do usuário",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "email": "usuario@exemplo.com",
                            "full_name": "Nome do Usuário",
                            "is_active": True,
                            "created_at": "2025-10-27T14:30:00Z",
                            "updated_at": "2025-10-27T15:00:00Z"
                        }
                    }
                },
            },
            401: {"description": "Token inválido ou expirado"},
        },
    )
    async def get_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        user = auth_service.get_user_from_token(token)
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }