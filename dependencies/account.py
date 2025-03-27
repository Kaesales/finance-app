from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService


def get_account_service(db: Session = Depends(get_db)):
    """Retorna uma instância do UserService."""
    account_repository = AccountRepository(db)
    return AccountService(account_repository)