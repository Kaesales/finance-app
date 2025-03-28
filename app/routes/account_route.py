from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.services.account_service import AccountService, AccountUpdate, AccountCreate
from app.schemas.account_schema import AccountResponse
from dependencies.account import get_account_service
from dependencies.auth import get_current_user
from app.models.user_model import User
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_current_user)]  
)

# --- CREATE ---
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_user)
):
    """Rota para criar uma conta"""
    try:
        return await account_service.create_account(account, current_user.id)
    except HTTPException as e:
        raise e
    
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
        
    except Exception as e:
        logger.critical("Erro interno ao criar conta:", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}"
        )

# --- UPDATE ---
@router.patch("/{account_id}")
async def update_account(
    account_id: int,
    update_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Rota para atualizar uma conta"""
    try:
        # Verifica se a conta pertence ao usuário
        if not await account_service.is_owner(account_id, current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Conta não é sua")

        result, message, data = await account_service.update_account(account_id, update_data)
        if not result:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=message)
        
        return {"message": message, "data": data}
    except Exception:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- DELETE ---
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_user)  
):
    """Rota para deletar uma conta"""
    try:
        # Verifica ownership antes de deletar
        if not await account_service.is_owner(account_id, current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Conta não é sua")

        success, message = await account_service.delete_account(account_id, current_user.id)
        if not success:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Falha ao deletar")
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        # Re-lançar exceções HTTP já tratadas
        raise
        
    except Exception as e:
        logger.critical("Erro crítico na exclusão:", exc_info=True)
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno no processamento"
            )
    

@router.get("")
async def list_accounts_user(
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_user)
):
    """Rota para listar contas de um usuário"""
    try:  
        accounts = await account_service.list_accounts(current_user.id)
        
        if not accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma conta encontrada para este usuário"
            )
        return accounts
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Erro inesperado ao listar contas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro inesperado ao listar contas"
        )