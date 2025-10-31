from fastapi import FastAPI
from app.controllers.auth_controller import AuthController

tags_metadata = [
    {
        "name": "auth",
        "description": "Operações de autenticação: login, verificação de token, etc.",
    },
    {
        "name": "usuários",
        "description": "Gerenciamento de usuários: criação, listagem, etc.",
    },
]

app = FastAPI(
        title="Async File Processing RAG API",
        description="API para processamento de documentos para preparação para RAG",
        version="alpha 0.0",
        openapi_tags=tags_metadata      
              )
app.include_router(AuthController.router)
