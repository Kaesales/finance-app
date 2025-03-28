from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError  
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.utils.auth import get_hash_password
import logging
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate):
        """Cria um novo usuário no banco de dados"""
        try:
            hashed_password = get_hash_password(user.password)  # Criptografa a senha

            # cria um objeto no banco de dados
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
            )
            
            self.db.add(db_user)
            await self.db.commit() 
            await self.db.refresh(db_user) 
            return db_user
        except SQLAlchemyError as e:
            logging.error(f"Erro ao criar usuário: {e}")
            raise
        except Exception as e: 
            await self.db.rollback()
            logging.error(f"Erro inesperado ao criar usuário: {e}")
            raise

    async def get_user_by_username(self, username: str):
        try:
            """Busca um usuário pelo nome de usuário"""
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar usuário pelo username: {e}")
            raise

    async def get_user_by_email(self, email: str) -> User | None:
        """Busca um usuário pelo email de usuário"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar user pelo email de usuário: {e}")
            raise

    async def verify_user_existence(self, username: str, email: str):
        try:
            result = await self.db.execute(
                select(User)
                .where(User.username==username)
                .where(User.email==email)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar user pelo email de usuário e username: {e}")
            raise