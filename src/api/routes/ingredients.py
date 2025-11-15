from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
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
async def create_ingredient(
    name: str = Form(...),
    quantity: str = Form(...),
    unit: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo ingrediente para o usuário autenticado
    
    - **name**: Nome do ingrediente (obrigatório)
    - **quantity**: Quantidade (obrigatório)
    - **unit**: Unidade de medida (obrigatório)
    - **image**: Arquivo de imagem (opcional) - JPEG, PNG ou WebP, máximo 5MB
    """
    ingredient_data = IngredientCreate(
        name=name,
        quantity=quantity,
        unit=unit
    )
    
    service = IngredientService(db)
    return await service.create_ingredient(ingredient_data, current_user.id, image)


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
async def update_ingredient(
    ingredient_id: str,
    name: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    unit: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um ingrediente existente
    
    - **ingredient_id**: ID do ingrediente
    - **name**: Nome do ingrediente (opcional)
    - **quantity**: Quantidade (opcional)
    - **unit**: Unidade de medida (opcional)
    - **image**: Nova imagem (opcional) - substituirá a anterior se fornecida
    """
    try:
        # Criar objeto de atualização apenas com campos fornecidos
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if quantity is not None:
            update_data["quantity"] = quantity
        if unit is not None:
            update_data["unit"] = unit
        
        ingredient_data = IngredientUpdate(**update_data)
        
        service = IngredientService(db)
        return await service.update_ingredient(
            UUID(ingredient_id), 
            current_user.id, 
            ingredient_data,
            image
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )


@router.delete("/{ingredient_id}", status_code=status.HTTP_200_OK)
async def delete_ingredient(
    ingredient_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um ingrediente e sua imagem associada
    
    - **ingredient_id**: ID do ingrediente
    """
    try:
        service = IngredientService(db)
        return await service.delete_ingredient(UUID(ingredient_id), current_user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )
