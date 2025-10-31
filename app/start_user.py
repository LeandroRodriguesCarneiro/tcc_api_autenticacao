from typing import Generator
from getpass import getpass
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.database.database import Database

# Função que cria o primeiro usuário
def create_first_user():
    db = Database.get_instance()
    session = db.get_session()

    while True:
        email = input('Digite o email do usuário: ')
        full_name = input('Digite o nome do usuário: ')
        
        # Usando getpass para esconder as senhas
        password = getpass('Digite a senha: ')
        confirm_password = getpass('Digite a senha novamente: ')

        if password != confirm_password:
            print('As senhas não coincidem. Digite novamente.')
            continue

        try:
            auth_service = AuthService(session)
            auth_service.add_user(email, password, full_name)
            print(f'Usuário {email} criado com sucesso!')
            session.close()
            break

        except Exception as e:
            print(f'Ocorreu um erro ao criar o usuário: {e}')

# Função principal de execução
if __name__ == "__main__":
    create_first_user()
