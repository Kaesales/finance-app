from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.utils.auth import get_hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserCreate):
        """Cria um novo usuário no banco de dados"""
        hashed_password = get_hash_password(user.password)  # Criptografa a senha

        # cria um objeto no banco de dados
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        await self.db.commit()  # Commit 
        await self.db.refresh(db_user)  # Refresh 
        return db_user

    async def get_user_by_username(self, username: str):
        """Busca um usuário pelo nome de usuário"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()
    

    async def get_user_by_email(self, email: str) -> User | None:
        """Busca um email pelo email de usuário"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()