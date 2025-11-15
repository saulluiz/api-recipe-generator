from sqlalchemy.orm import Session
from src.repositories.recipe_repository import RecipeRepository
from src.api.schemas.recipe_schema import (
    RecipeCreate, 
    RecipeResponse, 
    RecipeListResponse,
    RecipeIngredientCreate
)
from typing import List
import json


class RecipeService:
    def __init__(self, db: Session):
        self.repository = RecipeRepository(db)

    def create_recipe(self, user_id: str, recipe_data: RecipeCreate) -> RecipeResponse:
        """Cria uma nova receita para o usuário."""
        # Converte os passos para JSON string
        instructions_json = recipe_data.instructions
        
        # Converte ingredientes para formato do repository
        ingredients = [
            {
                'name': ing.name,
                'quantity': ing.quantity,
                'order': ing.order
            }
            for ing in recipe_data.ingredients
        ]

        recipe = self.repository.create(
            user_id=user_id,
            name=recipe_data.name,
            instructions=instructions_json,
            ingredients=ingredients
        )

        # Converter UUIDs para strings antes de validar
        recipe_dict = {
            'id': str(recipe.id),
            'user_id': str(recipe.user_id),
            'name': recipe.name,
            'instructions': recipe.instructions,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'recipe_ingredients': [
                {
                    'id': str(ing.id),
                    'recipe_id': str(ing.recipe_id),
                    'name': ing.name,
                    'quantity': ing.quantity,
                    'order': ing.order
                }
                for ing in recipe.recipe_ingredients
            ]
        }

        return RecipeResponse.model_validate(recipe_dict)

    def get_recipe(self, recipe_id: str, user_id: str) -> RecipeResponse:
        """Busca uma receita específica."""
        recipe = self.repository.get_by_id(recipe_id)
        
        if not recipe:
            raise ValueError("Receita não encontrada")
        
        if str(recipe.user_id) != user_id:
            raise PermissionError("Você não tem permissão para acessar esta receita")
        
        # Converter UUIDs para strings
        recipe_dict = {
            'id': str(recipe.id),
            'user_id': str(recipe.user_id),
            'name': recipe.name,
            'instructions': recipe.instructions,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'recipe_ingredients': [
                {
                    'id': str(ing.id),
                    'recipe_id': str(ing.recipe_id),
                    'name': ing.name,
                    'quantity': ing.quantity,
                    'order': ing.order
                }
                for ing in recipe.recipe_ingredients
            ]
        }
        
        return RecipeResponse.model_validate(recipe_dict)

    def list_user_recipes(self, user_id: str) -> List[RecipeListResponse]:
        """Lista todas as receitas do usuário."""
        recipes = self.repository.get_by_user_id(user_id)
        
        return [
            RecipeListResponse(
                id=str(recipe.id),
                name=recipe.name,
                created_at=recipe.created_at,
                ingredients_count=len(recipe.recipe_ingredients)
            )
            for recipe in recipes
        ]

    def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        """Deleta uma receita do usuário."""
        recipe = self.repository.get_by_id(recipe_id)
        
        if not recipe:
            raise ValueError("Receita não encontrada")
        
        if str(recipe.user_id) != user_id:
            raise PermissionError("Você não tem permissão para deletar esta receita")
        
        return self.repository.delete(recipe_id)
