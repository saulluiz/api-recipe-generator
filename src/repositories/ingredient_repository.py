from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID

from src.models.ingredient import Ingredient
from src.api.schemas.ingredient_schema import IngredientCreate, IngredientUpdate


class IngredientRepository:
    """Repository para gerenciar operações de Ingredientes no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ingredient_data: IngredientCreate, user_id: UUID, image_path: Optional[str] = None) -> Ingredient:
        """Cria um novo ingrediente no banco de dados"""
        try:
            db_ingredient = Ingredient(
                name=ingredient_data.name,
                quantity=ingredient_data.quantity,
                unit=ingredient_data.unit,
                image_url=image_path,
                user_id=user_id
            )
            self.db.add(db_ingredient)
            self.db.commit()
            self.db.refresh(db_ingredient)
            return db_ingredient
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, ingredient_id: UUID, user_id: UUID) -> Optional[Ingredient]:
        """Busca um ingrediente por ID e verifica se pertence ao usuário"""
        return self.db.query(Ingredient).filter(
            Ingredient.id == ingredient_id,
            Ingredient.user_id == user_id
        ).first()
    
    def get_all_by_user(self, user_id: UUID) -> List[Ingredient]:
        """Retorna todos os ingredientes de um usuário"""
        return self.db.query(Ingredient).filter(
            Ingredient.user_id == user_id
        ).order_by(Ingredient.created_at.desc()).all()
    
    def update(
        self, 
        ingredient_id: UUID, 
        user_id: UUID, 
        ingredient_data: IngredientUpdate
    ) -> Optional[Ingredient]:
        """Atualiza um ingrediente existente"""
        db_ingredient = self.get_by_id(ingredient_id, user_id)
        
        if not db_ingredient:
            return None
        
        # Atualiza apenas os campos fornecidos
        update_data = ingredient_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ingredient, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_ingredient)
            return db_ingredient
        except IntegrityError as e:
            self.db.rollback()
            raise e
    
    def delete(self, ingredient_id: UUID, user_id: UUID) -> bool:
        """Remove um ingrediente do banco de dados"""
        db_ingredient = self.get_by_id(ingredient_id, user_id)
        
        if not db_ingredient:
            return False
        
        try:
            self.db.delete(db_ingredient)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
