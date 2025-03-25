# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..schemas.token_schema import Token, LoginRequest
from ..services.user_service import UserService
from dependencies.user import get_user_service
from ..utils.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    credentials: LoginRequest, 
    user_service: UserService = Depends(get_user_service)
):
    '''
    Endpoint de autenticação que gera tokens JWT para usuários válidos.

    Args:
        credentials (LoginRequest): Objeto contendo username e password.
        user_service (UserService): Serviço injetado para validação de usuários.

    Returns:
        Token: Objeto contendo access_token e token_type.

    Raises:
        HTTPException: 401 Unauthorized se as credenciais forem inválidas.

    Examples:
        >>> Request (JSON):
        {
            "username": "usuario123",
            "password": "senhaSegura123"
        }
        
        >>> Response (Success):
        {
            "access_token": "eyJhbGciOi...",
            "token_type": "bearer"
        }
        
        >>> Response (Error):
        {
            "detail": "Usuário ou senha incorretos"
        }
    '''
    # Autentica o usuário
    user = await user_service.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o token JWT (expira em 30 minutos por padrão)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # "sub" é o subject padrão do JWT
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}