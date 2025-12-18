"""
Système de recommandation de produits alternatifs.
"""

from typing import List, Dict, Any, Optional
from .llm_manager import LLMManager
from .prompts import NutritionPrompts


class ProductRecommender:
    """Recommande des alternatives alimentaires plus saines."""

    def __init__(self, llm_manager: Optional[LLMManager] = None):
        self.llm = llm_manager or LLMManager()
        self.prompts = NutritionPrompts()

    def recommend(
        self,
        original_product: Dict[str, Any],
        candidate_products: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Recommande des alternatives à un produit.

        Args:
            original_product: Produit initial
            candidate_products: Produits comparables (OpenFoodFacts)
            preferences: Préférences utilisateur (bio, vegan, sans gluten…)
            model: Modèle LLM

        Returns:
            Recommandations IA
        """
        preferences = preferences or {}

        messages = [
            {
                "role": "system",
                "content": self.prompts.recommendation_system_prompt()
            },
            {
                "role": "user",
                "content": self.prompts.recommendation_user_prompt(
                    original_product,
                    candidate_products,
                    preferences
                )
            }
        ]

        try:
            response, model_used = self.llm.complete_with_fallback(
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )

            return {
                "success": True,
                "recommendations": response,
                "model_used": model_used
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def filter_healthier_products(
        products: List[Dict[str, Any]],
        max_nutriscore: str = "B"
    ) -> List[Dict[str, Any]]:
        """
        Filtrage simple sans IA (pré-traitement).
        """
        allowed = ["A", "B", "C", "D", "E"]
        threshold = allowed.index(max_nutriscore)

        return [
            p for p in products
            if p.get("nutriscore_grade")
            and allowed.index(p["nutriscore_grade"].upper()) <= threshold
        ]
