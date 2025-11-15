from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.models.recipe import Recipe
from src.models.recipe_ingredient import RecipeIngredient
from typing import List, Optional
import json


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, name: str, instructions: str, ingredients: List[dict]) -> Recipe:
        """
        Cria uma nova receita com seus ingredientes.
        
        Args:
            user_id: ID do usuário
            name: Nome da receita
            instructions: JSON string com os passos da receita
            ingredients: Lista de dicts com 'name', 'quantity', 'order'
        """
        # Cria a receita
        recipe = Recipe(
            user_id=user_id,
            name=name,
            instructions=instructions
        )
        self.db.add(recipe)
        self.db.flush()  # Garante que o recipe.id seja gerado

        # Cria os ingredientes da receita
        for ing_data in ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                name=ing_data['name'],
                quantity=ing_data['quantity'],
                order=ing_data.get('order', 0)
            )
            self.db.add(recipe_ingredient)

        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Busca uma receita por ID."""
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

    def get_by_user_id(self, user_id: str) -> List[Recipe]:
        """Lista todas as receitas de um usuário."""
        return (
            self.db.query(Recipe)
            .filter(Recipe.user_id == user_id)
            .order_by(desc(Recipe.created_at))
            .all()
        )

    def delete(self, recipe_id: str) -> bool:
        """Deleta uma receita."""
        recipe = self.get_by_id(recipe_id)
        if recipe:
            self.db.delete(recipe)
            self.db.commit()
            return True
        return False

    def update(self, recipe_id: str, name: Optional[str] = None, 
               instructions: Optional[str] = None) -> Optional[Recipe]:
        """Atualiza uma receita."""
        recipe = self.get_by_id(recipe_id)
        if recipe:
            if name:
                recipe.name = name
            if instructions:
                recipe.instructions = instructions
            self.db.commit()
            self.db.refresh(recipe)
        return recipe
