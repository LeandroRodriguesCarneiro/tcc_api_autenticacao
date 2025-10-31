from jwt import JWT, jwk_from_dict, exceptions
from time import time
from app.config import Settings

class JWTHandler:
    def __init__(self):
        self.jwt = JWT()
        self.secret_key = jwk_from_dict({"k": Settings.SECRET_KEY, "kty": "oct"})

    def create_token(self, payload: dict, expires_in: int) -> str:
        payload_to_encode = payload.copy()
        payload_to_encode["exp"] = int(time() + expires_in)
        return self.jwt.encode(payload_to_encode, self.secret_key, alg=Settings.ALGORITHM)

    def create_tokens_pair(self, email: str, token_version: int) -> dict:
        """
        Cria um par de tokens: access_token (curto) e refresh_token (longo).
        """
        access_token = self.create_token(
            {"sub": email, "type": "access", "token_version": token_version},
            Settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        refresh_token = self.create_token(
            {"sub": email, "type": "refresh", "token_version": token_version},
            Settings.ACCESS_TOKEN_EXPIRE_HOURS,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def decoded_token(self, token: str) -> dict | None:
        try:
            decoded = self.jwt.decode(token, self.secret_key, do_verify=True)
            if "exp" in decoded and decoded["exp"] < time():
                raise exceptions.JWTException("Token expirado")
            return decoded
        except Exception as e:
            print(e)
            return None
