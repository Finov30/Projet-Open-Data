"""
Analyse nutritionnelle automatisée d'un produit.
"""

from typing import Dict, Any, Optional
from .llm_manager import LLMManager
from .prompts import NutritionPrompts


class ProductAnalyzer:
    """Analyse un produit alimentaire via IA."""

    def __init__(self, llm_manager: Optional[LLMManager] = None):
        self.llm = llm_manager or LLMManager()
        self.prompts = NutritionPrompts()

    def analyze(
        self,
        product: Dict[str, Any],
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Analyse complète d'un produit alimentaire.

        Args:
            product: Données OpenFoodFacts du produit
            model: Modèle LLM à utiliser

        Returns:
            Résultat d'analyse structuré
        """
        messages = [
            {
                "role": "system",
                "content": self.prompts.product_analysis_system_prompt()
            },
            {
                "role": "user",
                "content": self.prompts.product_analysis_user_prompt(product)
            }
        ]

        try:
            response, model_used = self.llm.complete_with_fallback(
                messages=messages,
                temperature=0.6,
                max_tokens=500
            )

            return {
                "success": True,
                "analysis": response,
                "model_used": model_used,
                "nutriscore": product.get("nutriscore_grade"),
                "nova_group": product.get("nova_group"),
                "product_name": product.get("product_name")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def quick_summary(
        self,
        product: Dict[str, Any]
    ) -> str:
        """
        Résumé rapide sans IA (fallback UX).
        """
        return (
            f"{product.get('product_name', 'Produit')} "
            f"(Nutri-Score {product.get('nutriscore_grade', '?').upper()}, "
            f"NOVA {product.get('nova_group', '?')})"
        )
