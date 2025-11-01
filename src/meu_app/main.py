from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import users

app = FastAPI(
    title="API Recipe Generator",
    description="API para gerenciar e gerar receitas culinárias com IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "API Recipe Generator is running"}