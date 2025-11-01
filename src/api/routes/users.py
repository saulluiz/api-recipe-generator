from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.api.schemas.user_schema import UserCreate, UserLogin, UserResponse, Token
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.api.middlewares.auth import get_current_user
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    user = user_service.register_user(user_data)
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    token = user_service.login_user(login_data)
    return token


@router.get("/me", response_model=UserResponse)
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user
