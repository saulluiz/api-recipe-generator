from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.database.connection import get_db
from src.api.middlewares.auth import get_current_user
from src.api.schemas.ingredient_schema import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse
)
from src.api.schemas.user_schema import UserResponse
from src.services.ingredient_service import IngredientService

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"]
)


@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    ingredient_data: IngredientCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo ingrediente para o usuário autenticado
    
    - **name**: Nome do ingrediente (obrigatório)
    - **quantity**: Quantidade (obrigatório)
    - **unit**: Unidade de medida (obrigatório)
    - **image_url**: URL da imagem (opcional)
    """
    service = IngredientService(db)
    return service.create_ingredient(ingredient_data, current_user.id)


@router.get("/", response_model=List[IngredientResponse])
def list_ingredients(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os ingredientes do usuário autenticado
    """
    service = IngredientService(db)
    return service.list_user_ingredients(current_user.id)


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca um ingrediente específico por ID
    
    - **ingredient_id**: ID do ingrediente
    """
    try:
        service = IngredientService(db)
        return service.get_ingredient(UUID(ingredient_id), current_user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )


@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: str,
    ingredient_data: IngredientUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um ingrediente existente
    
    - **ingredient_id**: ID do ingrediente
    - Todos os campos são opcionais
    """
    try:
        service = IngredientService(db)
        return service.update_ingredient(
            UUID(ingredient_id), 
            current_user.id, 
            ingredient_data
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )


@router.delete("/{ingredient_id}", status_code=status.HTTP_200_OK)
def delete_ingredient(
    ingredient_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um ingrediente
    
    - **ingredient_id**: ID do ingrediente
    """
    try:
        service = IngredientService(db)
        return service.delete_ingredient(UUID(ingredient_id), current_user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )
