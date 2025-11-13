from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from fastapi import HTTPException, status

from src.repositories.ingredient_repository import IngredientRepository
from src.api.schemas.ingredient_schema import (
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse
)


class IngredientService:
    """Service para gerenciar a lógica de negócio de Ingredientes"""
    
    def __init__(self, db: Session):
        self.repository = IngredientRepository(db)
    
    def create_ingredient(
        self, 
        ingredient_data: IngredientCreate, 
        user_id: UUID
    ) -> IngredientResponse:
        """Cria um novo ingrediente"""
        try:
            ingredient = self.repository.create(ingredient_data, user_id)
            return IngredientResponse.model_validate(ingredient)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar ingrediente: {str(e)}"
            )
    
    def get_ingredient(self, ingredient_id: UUID, user_id: UUID) -> IngredientResponse:
        """Busca um ingrediente por ID"""
        ingredient = self.repository.get_by_id(ingredient_id, user_id)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        return IngredientResponse.model_validate(ingredient)
    
    def list_user_ingredients(self, user_id: UUID) -> List[IngredientResponse]:
        """Lista todos os ingredientes de um usuário"""
        ingredients = self.repository.get_all_by_user(user_id)
        return [IngredientResponse.model_validate(ing) for ing in ingredients]
    
    def update_ingredient(
        self, 
        ingredient_id: UUID, 
        user_id: UUID, 
        ingredient_data: IngredientUpdate
    ) -> IngredientResponse:
        """Atualiza um ingrediente existente"""
        ingredient = self.repository.update(ingredient_id, user_id, ingredient_data)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        return IngredientResponse.model_validate(ingredient)
    
    def delete_ingredient(self, ingredient_id: UUID, user_id: UUID) -> dict:
        """Remove um ingrediente"""
        success = self.repository.delete(ingredient_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        return {"message": "Ingrediente removido com sucesso"}
