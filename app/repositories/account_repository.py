from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError  
from app.models.account_model import Account
from app.schemas.account_schema import AccountResponse, AccountCreate, AccountUpdate, AccountType
from typing import Optional, List
import logging 

class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, account: AccountCreate):
        """Cria uma conta que pode ser de débito ou crédito"""
        try:
            db_account = Account(**account.model_dump()) 
            self.db.add(db_account)
            await self.db.commit()
            await self.db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:  
            await self.db.rollback()
            logging.error(f"Erro ao criar conta no banco: {e}")
            raise
        except Exception as e: 
            await self.db.rollback()
            logging.error(f"Erro inesperado ao criar conta: {e}")
            raise
        
    async def get_by_id(self, account_id: int):
        """Retorna uma conta a partir de um ID"""
        try:
            return await self.db.get(Account, account_id)
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar conta {account_id}: {e}")
            raise

    async def get_by_name_and_user(self, name: str, user_id: int):
        """Retorna uma conta com nome e user fornecidos"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.name == name)
                .where(Account.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar conta por nome: {e}")
            raise

    async def get_all_by_user(self, user_id: int):
        """Retorna todas as contas referentes a um User"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.user_id == user_id)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar contas do usuário {user_id}: {e}")
            raise
    
    async def get_by_id_and_user(self, account_id, user_id):
        """Retorna uma conta com ID e user fornecidos"""
        try:
            result = await self.db.execute(
                select(Account)
                .where(Account.id == account_id)
                .where(Account.user_id == user_id)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logging.error(f"Erro ao buscar conta {account_id} do usuário {user_id}: {e}")
            raise

    async def update(self, account_id, update_data: AccountUpdate):
        """Atualiza a conta de um User"""
        try:
            db_account = await self.db.get(Account, account_id)
            if not db_account:
                return None
                
            update_dict = update_data.model_dump(exclude_unset=True)
        
            for key, value in update_dict.items():
                setattr(db_account, key, value)
                
            await self.db.commit()
            await self.db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Erro ao atualizar conta {account_id}: {e}")
            raise

    async def delete(self, account_id: int):
        """Deleta a Conta de um User"""
        try:
            await self.db.execute(
                delete(Account).where(Account.id == account_id)
            )
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.error(f"Erro ao deletar conta {account_id}: {e}")
            raise