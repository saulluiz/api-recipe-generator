from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api.routes import users, ingredients, recipes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização do servidor"""
    logger.info("🚀 API Recipe Generator está iniciando...")
    logger.info("✅ Servidor pronto para receber requisições")

app.include_router(users.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)


@app.get("/")
def root():
    return {"message": "API Recipe Generator is running"}

@app.get("/health")
def health_check():
    """Endpoint de health check simples"""
    return {"status": "ok", "message": "API is healthy"}