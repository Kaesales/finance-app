from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import user_routes, auth, account_route

# Cria uma instância do FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Inclui as rotas de usuários
app.include_router(user_routes.router)
app.include_router(auth.router)
app.include_router(account_route.router)

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

