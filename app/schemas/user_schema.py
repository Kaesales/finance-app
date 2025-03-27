from pydantic import BaseModel, EmailStr, SecretStr

# Schema de entrada (API → Service)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  

# Schema de resposta (API → Cliente)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # Permite conversão de ORM para Pydantic