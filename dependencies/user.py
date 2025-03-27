from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_user_service(db: Session = Depends(get_db)):
    """Retorna uma instância do UserService."""
    user_repository = UserRepository(db)
    return UserService(user_repository)

