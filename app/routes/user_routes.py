from fastapi import APIRouter, Depends, HTTPException
from ..schemas.user_schema import UserCreate, UserResponse
from ..services.user_service import UserService
from dependencies.user import get_user_service

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)  # Injeção do UserService
):
    """Rota para criar um novo usuário."""
    try:
        return await user_service.create_user(user) 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/users/{username}", response_model=UserResponse)
async def read_user(
    username: str,
    user_service: UserService = Depends(get_user_service)  # Injeção do UserService
):
    """Rota para buscar um usuário pelo nome de usuário."""
    db_user = await user_service.get_user_by_username(username)  # Chamada assíncrona
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user