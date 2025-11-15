from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Schema para ingrediente na receita gerada pela IA (em português)
class RecipeIngredientGenerated(BaseModel):
    nome: str
    quantidade: str


# Schema para ingrediente na receita do banco (em inglês)
class RecipeIngredientBase(BaseModel):
    name: str
    quantity: str


class RecipeIngredientCreate(RecipeIngredientBase):
    order: int = 0


class RecipeIngredientResponse(RecipeIngredientBase):
    id: str
    recipe_id: str
    order: int

    class Config:
        from_attributes = True


# Schema para passo da receita
class RecipeStep(BaseModel):
    numero: int
    descricao: str


# Schema para request de geração de receita
class GenerateRecipeRequest(BaseModel):
    listaIngredientes: List[dict]  # [{"Ingrediente": "Tomate", "qtd": "2 unidades"}]


# Schema para resposta da IA
class GeneratedRecipe(BaseModel):
    nome: str
    listaIngredientes: List[RecipeIngredientGenerated]
    passos: List[RecipeStep]


class GenerateRecipeResponse(BaseModel):
    listaReceitas: List[GeneratedRecipe]


# Schema para criar receita no banco
class RecipeCreate(BaseModel):
    name: str
    instructions: str  # JSON string dos passos
    ingredients: List[RecipeIngredientCreate]


# Schema para resposta de receita
class RecipeResponse(BaseModel):
    id: str
    user_id: str
    name: str
    instructions: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    recipe_ingredients: List[RecipeIngredientResponse] = []

    class Config:
        from_attributes = True


# Schema para listar receitas (versão simplificada)
class RecipeListResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    ingredients_count: int

    class Config:
        from_attributes = True
