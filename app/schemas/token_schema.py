# schemas/token_schema.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):  # Schema para a resposta
    access_token: str
    token_type: str