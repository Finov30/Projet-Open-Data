"""
Chatbot conversationnel pour répondre aux questions sur la nutrition.
"""
from typing import Dict, List, Optional, Any
from .llm_manager import LLMManager
from .prompts import NutritionPrompts


class NutritionChatbot:
    """Chatbot intelligent pour répondre aux questions nutritionnelles."""

    def __init__(self, llm_manager: Optional[LLMManager] = None):
        """
        Initialise le chatbot.

        Args:
            llm_manager: Instance du gestionnaire LLM
        """
        self.llm = llm_manager or LLMManager()
        self.prompts = NutritionPrompts()
        self.conversation_history: List[Dict[str, str]] = []

    def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Répond à un message utilisateur.

        Args:
            user_message: Message de l'utilisateur
            context: Contexte additionnel (produit en cours de consultation, etc.)
            stream: Si True, retourne un générateur pour streaming

        Returns:
            Réponse du chatbot
        """
        # Prépare le contexte
        context_str = ""
        if context and "current_product" in context:
            product = context["current_product"]
            context_str = (
                f"\n\nProduit en consultation : {product.get('product_name', 'Inconnu')}"
                f"\nNutri-Score : {product.get('nutriscore_grade', '?')}"
                f"\nNOVA : {product.get('nova_group', '?')}"
            )

        # Construit les messages
        messages = [
            {"role": "system", "content": self.prompts.chatbot_system_prompt()}
        ]

        # Historique limité
        messages.extend(self.conversation_history[-10:])

        messages.append({
            "role": "user",
            "content": user_message + context_str
        })

        try:
            response = self.llm.complete(
                messages=messages,
                temperature=0.7,
                max_tokens=400,
                stream=stream
            )

            if stream:
                return {
                    "success": True,
                    "stream": response,
                    "model_used": self.llm.default_model
                }

            # Mise à jour historique
            self.conversation_history.append(
                {"role": "user", "content": user_message}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response}
            )

            return {
                "success": True,
                "response": response,
                "model_used": self.llm.default_model,
                "message_count": len(self.conversation_history)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def clear_history(self):
        """Efface l'historique de conversation."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique de conversation."""
        return self.conversation_history.copy()

    def ask_about_ingredient(self, ingredient: str) -> Dict[str, Any]:
        question = (
            f"Peux-tu m'expliquer ce qu'est {ingredient} "
            f"et s'il faut l'éviter d'un point de vue nutritionnel ?"
        )
        return self.chat(question)

    def ask_about_allergen(self, allergen: str) -> Dict[str, Any]:
        question = (
            f"Je suis allergique au {allergen}. "
            f"Quels produits dois-je éviter et quelles alternatives existent ?"
        )
        return self.chat(question)

    def get_quick_answer(self, question: str) -> str:
        messages = [
            {"role": "system", "content": self.prompts.chatbot_system_prompt()},
            {"role": "user", "content": question}
        ]

        try:
            return self.llm.complete(
                messages=messages,
                temperature=0.6,
                max_tokens=200
            )
        except Exception as e:
            return f"Erreur : {str(e)}"

    def suggest_questions(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        base_questions = [
            "🍎 C'est quoi le Nutri-Score exactement ?",
            "🔬 Qu'est-ce qu'un additif alimentaire ?",
            "🥗 Comment composer un repas équilibré ?",
            "⚠️ Quels sont les allergènes les plus courants ?",
            "🏷️ C'est quoi un produit bio ?"
        ]

        if context and "current_product" in context:
            product = context["current_product"]
            contextual = []

            if product.get("nutriscore_grade"):
                contextual.append(
                    f"Pourquoi ce produit a un Nutri-Score {product['nutriscore_grade']} ?"
                )

            if product.get("additives_n", 0) > 0:
                contextual.append(
                    "Les additifs de ce produit sont-ils préoccupants ?"
                )

            if product.get("allergens"):
                contextual.append(
                    "Quels allergènes contient ce produit ?"
                )

            if product.get("nova_group"):
                contextual.append(
                    f"Que signifie le groupe NOVA {product['nova_group']} ?"
                )

            return contextual + base_questions

        return base_questions

    def explain_score(
        self,
        score_type: str,
        score_value: Any,
        product_name: str = ""
    ) -> Dict[str, Any]:
        product_str = f" pour {product_name}" if product_name else ""
        question = (
            f"Peux-tu m'expliquer le score {score_type.upper()} "
            f"{score_value}{product_str} ?"
        )
        return self.chat(question)
