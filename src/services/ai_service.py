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

    async def generate_recipe(self, ingredients: List[dict], exclude_recipes: List[str] = None) -> GeneratedRecipe:
        """
        Gera uma receita usando Groq (Llama 3.3) baseado nos ingredientes fornecidos.
        
        Args:
            ingredients: Lista de dicts com formato [{"Ingrediente": "Tomate", "qtd": "2 unidades"}]
            exclude_recipes: Lista de nomes de receitas que NÃO devem ser geradas novamente
        
        Returns:
            GeneratedRecipe com nome, lista de ingredientes e passos
        """
        # Formata a lista de ingredientes para o prompt
        ingredients_text = "\n".join([
            f"- {ing['Ingrediente']}: {ing['qtd']}" 
            for ing in ingredients
        ])

        # Adiciona restrições de receitas excluídas
        exclusion_text = ""
        if exclude_recipes:
            exclusion_text = f"\n\nIMPORTANTE: NÃO crie nenhuma das seguintes receitas:\n" + "\n".join([f"- {recipe}" for recipe in exclude_recipes])

        # Prompt para o Groq
        prompt = f"""Você é um chef especializado em criar receitas deliciosas.

Com base nos seguintes ingredientes disponíveis, crie UMA receita completa e saborosa:

{ingredients_text}{exclusion_text}

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

    async def generate_multiple_recipes(self, ingredients: List[dict], count: int = 5) -> List[GeneratedRecipe]:
        """
        Gera múltiplas receitas diferentes usando requisições sequenciais à LLM.
        Cada receita subsequente exclui as anteriores para garantir variedade.
        
        Args:
            ingredients: Lista de dicts com formato [{"Ingrediente": "Tomate", "qtd": "2 unidades"}]
            count: Número de receitas a gerar (padrão: 5)
        
        Returns:
            List[GeneratedRecipe]: Lista com as receitas geradas
        """
        recipes = []
        exclude_list = []
        
        for i in range(count):
            try:
                # Gera receita com restrições das anteriores
                recipe = await self.generate_recipe(ingredients, exclude_recipes=exclude_list if exclude_list else None)
                recipes.append(recipe)
                
                # Adiciona o nome da receita à lista de exclusão
                exclude_list.append(recipe.nome)
                
            except Exception as e:
                print(f"Erro ao gerar receita {i+1}/{count}: {str(e)}")
                # Continua tentando gerar as próximas mesmo se uma falhar
                continue
        
        return recipes


# Instância única do serviço
ai_service = AIService()
