from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse
from typing import Optional, Tuple, Dict, Any, List
from app.models.user_model import User
from app.utils.auth import verify_password, get_hash_password
from fastapi import HTTPException, status
import logging

class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def create_user(self, user: UserCreate):
        """Cria um novo usuário"""
        try:
            # Verifica se o usuário já está cadastrado
            if await self.user_repository.verify_user_existence(user.username, user.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário já cadastrado",
                )

            # Verifica se o username existe
            if await self.user_repository.get_user_by_username(user.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username já cadastrado",
                )

            # Verifica se o email está sendo usado
            if await self.user_repository.get_user_by_email(user.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado",
                )

            return await self.user_repository.create_user(user)

        except HTTPException as e:
            # Lida com exceções HTTP específicas
            logging.error(f"Erro HTTP: {e.detail}")
            raise e  # Relança a exceção para ser tratada pela camada superior
        except Exception as e:
            # Captura outros erros inesperados
            logging.error(f"Erro inesperado ao criar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro inesperado ao criar usuário",
            )

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            # Busca o usuário no banco de dados
            user = await self.user_repository.get_user_by_username(username)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Verifica se a senha fornecida está correta
            if not verify_password(password, user.hashed_password):
                raise ValueError("Senha incorreta")
            
            return user

        except ValueError as e:
            # Captura erros específicos de validação
            logging.error(f"Erro de autenticação: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            # Captura outros erros inesperados
            logging.error(f"Erro inesperado ao autenticar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro inesperado ao autenticar usuário",
            )
