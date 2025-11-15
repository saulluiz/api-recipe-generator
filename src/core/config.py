from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_DB_URL: str
    SECRET_KEY: str
    OPENAI_API_KEY: str = ""  # Opcional: se não usar OpenAI
    GROQ_API_KEY: str = ""    # Opcional: se não usar Groq
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
