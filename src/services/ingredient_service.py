from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status, UploadFile

from src.repositories.ingredient_repository import IngredientRepository
from src.services.storage_service import StorageService
from src.api.schemas.ingredient_schema import (
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse
)


class IngredientService:
    
    def __init__(self, db: Session):
        self.repository = IngredientRepository(db)
        self.storage_service = StorageService()
    
    async def create_ingredient(
        self, 
        ingredient_data: IngredientCreate, 
        user_id: UUID,
        image_file: Optional[UploadFile] = None
    ) -> IngredientResponse:
        image_path = None
        
        if image_file:
            try:
                image_path = await self.storage_service.upload_image(image_file)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao processar imagem: {str(e)}"
                )
        
        try:
            ingredient = self.repository.create(ingredient_data, user_id, image_path)
            response = IngredientResponse.model_validate(ingredient)
            
            if ingredient.image_url:
                response.image_url = self.storage_service.get_public_url(ingredient.image_url)
            
            return response
        except Exception as e:
            if image_path:
                await self.storage_service.delete_image(image_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar ingrediente: {str(e)}"
            )
    
    def get_ingredient(self, ingredient_id: UUID, user_id: UUID) -> IngredientResponse:
        ingredient = self.repository.get_by_id(ingredient_id, user_id)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        response = IngredientResponse.model_validate(ingredient)
        
        if ingredient.image_url:
            response.image_url = self.storage_service.get_public_url(ingredient.image_url)
        
        return response
    
    def list_user_ingredients(self, user_id: UUID) -> List[IngredientResponse]:
        ingredients = self.repository.get_all_by_user(user_id)
        responses = []
        
        for ing in ingredients:
            response = IngredientResponse.model_validate(ing)
            if ing.image_url:
                response.image_url = self.storage_service.get_public_url(ing.image_url)
            responses.append(response)
        
        return responses
    
    async def update_ingredient(
        self, 
        ingredient_id: UUID, 
        user_id: UUID, 
        ingredient_data: IngredientUpdate,
        image_file: Optional[UploadFile] = None
    ) -> IngredientResponse:
        existing = self.repository.get_by_id(ingredient_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        old_image_path = existing.image_url
        new_image_path = None
        
        if image_file:
            try:
                new_image_path = await self.storage_service.upload_image(image_file)
                existing.image_url = new_image_path
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao processar imagem: {str(e)}"
                )
        
        ingredient = self.repository.update(ingredient_id, user_id, ingredient_data)
        
        if not ingredient:
            if new_image_path:
                await self.storage_service.delete_image(new_image_path)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        if new_image_path and old_image_path:
            await self.storage_service.delete_image(old_image_path)
        
        response = IngredientResponse.model_validate(ingredient)
        
        if ingredient.image_url:
            response.image_url = self.storage_service.get_public_url(ingredient.image_url)
        
        return response
    
    async def delete_ingredient(self, ingredient_id: UUID, user_id: UUID) -> dict:
        ingredient = self.repository.get_by_id(ingredient_id, user_id)
        
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        image_path = ingredient.image_url
        
        success = self.repository.delete(ingredient_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente não encontrado"
            )
        
        if image_path:
            await self.storage_service.delete_image(image_path)
        
        return {"message": "Ingrediente removido com sucesso"}
