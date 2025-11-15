from fastapi import HTTPException, status
from uuid import UUID
from src.repositories.user_repository import UserRepository
from src.api.schemas.user_schema import UserCreate, UserLogin
from src.core.security import create_access_token


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, user_data: UserCreate):
        existing_user = self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        existing_email = self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        user = self.user_repository.create(user_data.model_dump())
        return user

    def login_user(self, login_data: UserLogin):
        user = self.user_repository.get_by_username(login_data.username)
        
        if not user or user.password != login_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email
        }
        access_token = create_access_token(data=token_data)
        
        return {"access_token": access_token, "token_type": "bearer"}

    def get_user_by_id(self, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
