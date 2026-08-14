from fastapi import FastAPI
from app.api.routes import router


# Cria a aplicação principal do VesteIA.
app = FastAPI()


# Registra na aplicação todas as rotas definidas em routes.py.
app.include_router(router)