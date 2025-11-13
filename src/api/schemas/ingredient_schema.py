from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class IngredientBase(BaseModel):
    """Schema base para Ingrediente"""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do ingrediente")
    quantity: str = Field(..., min_length=1, max_length=50, description="Quantidade")
    unit: str = Field(..., min_length=1, max_length=20, description="Unidade de medida")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem")


class IngredientCreate(IngredientBase):
    """Schema para criar um ingrediente"""
    pass


class IngredientUpdate(BaseModel):
    """Schema para atualizar um ingrediente"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[str] = Field(None, min_length=1, max_length=50)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)


class IngredientResponse(IngredientBase):
    """Schema de resposta para Ingrediente"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Anteriormente orm_mode = True no Pydantic v1
        json_encoders = {
            UUID: str  # Converte UUID para string no JSON
        }
