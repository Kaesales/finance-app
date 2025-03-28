from decimal import Decimal, InvalidOperation
from fastapi import HTTPException, status
from typing import Optional, Tuple, Dict, Any, List
from app.schemas.account_schema import AccountCreate, AccountUpdate, AccountResponse
from app.models.account_model import Account
from app.repositories.account_repository import AccountRepository
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import IntegrityError

import logging

logger = logging.getLogger(__name__)
class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.repository = account_repository

    async def create_account(self, account_data: AccountCreate, user_id: int) -> AccountResponse:
        """
        Cria nova conta com validações robustas
        - Verifica nome duplicado
        - Valida campos de crédito
        - Trata erros do banco
        """
        try:
            account_dict = account_data.model_dump()
            account_dict["user_id"] = user_id

            # Verificação de nome duplicado
            if await self.repository.get_by_name_and_user(account_data.name, user_id):
                raise ValueError("Já existe uma conta com este nome")
            

            # Validação de campos para crédito
            if account_data.is_credit:
                if not account_data.credit_limit or account_data.credit_limit == 0:
                    raise ValueError("Contas de crédito requerem um limite")
                
                if account_data.balance is not None:
                    raise ValueError("Contas de Crédito não possuem saldo")
                
                if account_data.due_day is None or not (1 <= account_data.due_day <= 31):
                    raise ValueError("Contas de crédito requerem data de vencimento e seu valor deve ser entre 1 e 31")
                
                try:
                    Decimal(str(account_data.credit_limit))
                except InvalidOperation:
                    raise ValueError("Formato inválido para limite de crédito")
            
            #validação de campos para débito
            else:
                if account_data.credit_limit is not None or account_data.due_day is not None:
                    raise ValueError("Contas de débito não possuem limite e data de vencimento")

                if account_data.balance is None:
                    raise ValueError("Contas de débito precisam do campo balance")

           
            return await self.repository.create(account_dict)

        except ValueError as ve:
            logger.warning(f"Validação falhou: {str(ve)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )

        except IntegrityError as e:
            logger.error(f"Erro de integridade: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma conta com este nome"
            )

        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar solicitação"
            )


    async def update_account(
        self,
        account_id: int,
        update_data: AccountUpdate,
    )-> Tuple[bool, str, Optional[Account]]:
        """Atualiza uma conta existente"""
        account = await self.repository.get_by_id(account_id)
        if not account:
           return False, "Conta não encontrada", {}, None

        # Aplica atualização
        try:
            if update_data.is_credit:
                if not update_data.credit_limit or update_data.credit_limit == 0:
                    raise ValueError("Contas de crédito requerem um limite")
                
                if update_data.balance is not None:
                    raise ValueError("Contas de Crédito não possuem saldo")
                
                if update_data.due_day is None or not (1 <= update_data.due_day <= 31):
                    raise ValueError("Contas de crédito requerem data de vencimento e seu valor deve ser entre 1 e 31")
                
                try:
                    Decimal(str(update_data.credit_limit))
                except InvalidOperation:
                    raise ValueError("Formato inválido para limite de crédito")
            
            #validação de campos para débito
            else:
                if update_data.credit_limit is not None or update_data.due_day is not None:
                    raise ValueError("Contas de débito não possuem limite e data de vencimento")

                if update_data.balance is None:
                    raise ValueError("Contas de débito precisam do campo balance")
                
            updated_account = await self.repository.update(account_id, update_data)
            return True, "Conta atualizada com sucesso", updated_account
        except ValueError as e:
            return False, f"Erro de validação: {str(e)}", None
    
        except Exception as e:
            return False, f"Erro ao atualizar conta: {str(e)}", None


    async def delete_account(self, account_id: int, user_id: int) -> Tuple[bool, str]:
        """Deleta uma conta com verificações"""

        account = await self.repository.get_by_id(account_id)

        if not account or account.user_id != user_id:
            return False, "Conta não encontrada ou não pertence ao usuário"

        try:
            await self.repository.delete(account_id)
            return True, "Conta excluída com sucesso"
        except Exception as e:
            return False, f"Erro ao excluir conta: {str(e)}"
        


    async def is_owner(self, account_id: int, user_id: int) -> bool:
        account = await self.repository.get_by_id_and_user(account_id, user_id)
        return account is not None
    

    async def list_accounts(self, user_id: int) -> List[Account]:
        try:
            accounts = await self.repository.get_all_by_user(user_id)
            if not accounts:
                logging.warning(f"Nenhuma conta encontrada para o usuário {user_id}")
            return accounts
        except Exception as e:
            logging.error(f"Erro ao listar contas para o usuário {user_id}: {str(e)}")
            raise