from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.api.middlewares.auth import get_current_user
from src.models.user import User
from src.services.ai_service import ai_service
from src.services.recipe_service import RecipeService
from src.api.schemas.recipe_schema import (
    GenerateRecipeRequest,
    GenerateRecipeResponse,
    GeneratedRecipe,
    RecipeCreate,
    RecipeResponse,
    RecipeListResponse,
    RecipeIngredientCreate
)
from typing import List
import json

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/generate", response_model=GenerateRecipeResponse)
async def generate_recipe(
    request: GenerateRecipeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Gera uma receita usando IA com base nos ingredientes fornecidos.
    """
    try:
        # Chama o serviço de IA
        generated_recipe = await ai_service.generate_recipe(request.listaIngredientes)
        
        # Retorna no formato esperado pelo frontend
        return GenerateRecipeResponse(
            listaReceitas=[generated_recipe]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar receita: {str(e)}"
        )


@router.post("/save", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def save_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Salva uma receita gerada no banco de dados do usuário.
    """
    try:
        print(f"=== SAVE RECIPE DEBUG ===")
        print(f"User ID: {current_user.id}")
        print(f"Recipe name: {recipe_data.name}")
        print(f"Instructions length: {len(recipe_data.instructions)}")
        print(f"Ingredients count: {len(recipe_data.ingredients)}")
        
        recipe_service = RecipeService(db)
        recipe = recipe_service.create_recipe(
            user_id=str(current_user.id),
            recipe_data=recipe_data
        )
        
        print(f"Recipe created successfully with ID: {recipe.id}")
        return recipe
    except Exception as e:
        print(f"ERROR saving recipe: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar receita: {str(e)}"
        )


@router.get("/", response_model=List[RecipeListResponse])
async def list_recipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as receitas salvas do usuário.
    """
    try:
        recipe_service = RecipeService(db)
        recipes = recipe_service.list_user_recipes(str(current_user.id))
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar receitas: {str(e)}"
        )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca uma receita específica do usuário.
    """
    try:
        recipe_service = RecipeService(db)
        recipe = recipe_service.get_recipe(recipe_id, str(current_user.id))
        return recipe
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar receita: {str(e)}"
        )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deleta uma receita do usuário.
    """
    try:
        recipe_service = RecipeService(db)
        recipe_service.delete_recipe(recipe_id, str(current_user.id))
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar receita: {str(e)}"
        )
