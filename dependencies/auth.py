from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.utils.auth import SECRET_KEY, ALGORITHM
from database.database import async_session  # Importe a sessão diretamente
from typing import Optional
import logging

# Configuração básica de logging
logger = logging.getLogger(__name__)

# OAuth2 com configurações seguras
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    auto_error=True
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Versão simplificada e segura sem get_async_session.
    - Valida o token JWT
    - Busca o usuário no banco
    - Trata erros específicos
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decodifica o token (valida estrutura e assinatura)
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]}  # Campos obrigatórios
        )
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception

        # 2. Busca o usuário (com sessão direta)
        async with async_session() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_username(username)
            
            if not user:
                raise credentials_exception

            logger.info('Esta é uma mensagem informativa')
            return user
            
    except JWTError as e:
        logger.warning(f"Token inválido: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao validar credenciais"
        )
    