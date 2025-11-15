from groq import Groq
from src.core.config import settings
from src.api.schemas.recipe_schema import GeneratedRecipe, RecipeIngredientGenerated, RecipeStep
import json
from typing import List


class AIService:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY não configurada no arquivo .env")
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def generate_recipe(self, ingredients: List[dict]) -> GeneratedRecipe:
        """
        Gera uma receita usando Groq (Llama 3.3) baseado nos ingredientes fornecidos.
        
        Args:
            ingredients: Lista de dicts com formato [{"Ingrediente": "Tomate", "qtd": "2 unidades"}]
        
        Returns:
            GeneratedRecipe com nome, lista de ingredientes e passos
        """
        # Formata a lista de ingredientes para o prompt
        ingredients_text = "\n".join([
            f"- {ing['Ingrediente']}: {ing['qtd']}" 
            for ing in ingredients
        ])

        # Prompt para o Groq
        prompt = f"""Você é um chef especializado em criar receitas deliciosas.

Com base nos seguintes ingredientes disponíveis, crie UMA receita completa e saborosa:

{ingredients_text}

IMPORTANTE: Retorne APENAS um objeto JSON válido sem nenhum texto adicional, seguindo exatamente este formato:

{{
  "nome": "Nome da Receita",
  "listaIngredientes": [
    {{"nome": "Nome do ingrediente", "quantidade": "quantidade com unidade"}},
    ...
  ],
  "passos": [
    {{"numero": 1, "descricao": "Descrição detalhada do primeiro passo"}},
    {{"numero": 2, "descricao": "Descrição detalhada do segundo passo"}},
    ...
  ]
}}

Regras:
1. Use TODOS os ingredientes fornecidos
2. Pode sugerir ingredientes básicos adicionais (sal, pimenta, óleo, água) se necessário
3. Crie entre 5-8 passos detalhados e claros
4. A receita deve ser realista e fácil de seguir
5. Retorne APENAS o JSON, sem markdown, sem explicações, sem código blocks"""

        try:
            # Chama a API da Groq
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente que retorna apenas JSON válido, sem formatação markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks se existirem
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse do JSON
            recipe_data = json.loads(content)

            # Converte para o schema Pydantic
            recipe = GeneratedRecipe(
                nome=recipe_data["nome"],
                listaIngredientes=[
                    RecipeIngredientGenerated(
                        nome=ing["nome"],
                        quantidade=ing["quantidade"]
                    ) for ing in recipe_data["listaIngredientes"]
                ],
                passos=[
                    RecipeStep(
                        numero=step["numero"],
                        descricao=step["descricao"]
                    ) for step in recipe_data["passos"]
                ]
            )

            return recipe

        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao processar resposta da IA: {str(e)}. Resposta: {content}")
        except Exception as e:
            raise Exception(f"Erro ao gerar receita com IA: {str(e)}")


# Instância única do serviço
ai_service = AIService()
