from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse
from app.utils.auth import verify_password, get_hash_password
from fastapi import HTTPException
from fastapi import status

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: UserCreate):
        """Cria um novo usuário"""
        
       # Verifica se username já existe
        existing_username = await self.user_repository.get_user_by_username(user.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já cadastrado",
            )

        # Verifica se email já existe
        existing_email = await self.user_repository.get_user_by_email(user.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )
        return await self.user_repository.create_user(user)  
        

    # usada para autenticar um usuário, verifica se o username fornecido existe no banco de dados e se a senha fornecida está correta
    async def authenticate_user(self, username: str, password: str):
        user = await self.user_repository.get_user_by_username(username)

        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user