from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..repositories import UserRepository
from ..security import JWTHandler, verify_password, hash_password
from ..dtos import UserDTO


class AuthService:
    def __init__(self, session: Session):
        self.repo = UserRepository(session)
        self.jwt = JWTHandler()

    def authenticate_user(self, email: str, password: str) -> dict:
        """
        Autentica um usuário pelo email e senha.
        Retorna um token JWT se autenticado.
        Lança HTTPException 401 se credenciais inválidas ou usuário bloqueado.
        """
        user = self.repo.get_by_email(email)

        if not user:
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

        if user.is_locked():
            raise HTTPException(
                status_code=403,
                detail=f"Usuário bloqueado até {user.locked_until.isoformat()}"
            )

        if not verify_password(password, user.hashed_password):
            user.login_attempts += 1
            user.updated_at = datetime.now(timezone.utc)

            if user.login_attempts >= self.repo.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + self.repo.LOCK_DURATION

            self.repo.session.commit()
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

        user.login_attempts = 0
        user.locked_until = None
        user.updated_at = datetime.now(timezone.utc)
        self.repo.session.commit()

        tokens = self.jwt.create_tokens_pair(email, user.token_version)
        return tokens

    def refresh_access_token(self, refresh_token: str) -> dict:
        decoded = self.jwt.decoded_token(refresh_token)
        if not decoded:
            raise Exception("Token inválido ou expirado")

        if decoded.get("type") != "refresh":
            raise Exception("Token não é do tipo refresh")

        email = decoded.get("sub")
        if not email:
            raise Exception("Token inválido: campo 'sub' ausente")

        user = self.repo.get_by_email(email)

        if not user:
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

        if user.is_locked():
            raise HTTPException(
                status_code=403,
                detail=f"Usuário bloqueado até {user.locked_until.isoformat()}"
            )

        user.token_version += 1
        self.repo.session.commit()

        tokens = self.jwt.create_tokens_pair(email, user.token_version)

        return tokens

    def add_user(self, email: str, password: str, full_name: str):
        """
        Cria um novo usuário com senha hashada.
        """
        existing_user = self.repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        hashed = hash_password(password)

        user_model = UserDTO(email=email, full_name=full_name, hashed_password=hashed, is_active=True)

        new_user = self.repo.add(user_model.to_model())

        return {"message": "Usuário criado com sucesso", "user_id": new_user.id}

    def change_password(self, email: str, old_password: str, new_password: str):
        """
        Troca a senha do usuário, após verificar a senha antiga.
        """
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Senha atual incorreta")

        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        user.token_version += 1
        self.repo.session.commit()

        return {"message": "Senha alterada com sucesso"}

    def delete_user(self, email: str):
        """
        Remove o usuário do banco de dados.
        """
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        self.repo.session.delete(user)
        self.repo.session.commit()

        return {"message": f"Usuário {email} deletado com sucesso"}

    def get_user_from_token(self, token: str):
        payload = self.jwt.decoded_token(token)
        if payload is None or "sub" not in payload or "token_version" not in payload:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        email = payload["sub"]
        token_version = payload["token_version"]
        user = self.repo.get_by_email(email)

        if not user or user.token_version != token_version:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        return user
