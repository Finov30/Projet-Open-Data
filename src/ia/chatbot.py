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
        model: str = "gpt-3.5-turbo",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Répond à un message utilisateur.
        
        Args:
            user_message: Message de l'utilisateur
            context: Contexte additionnel (produit en cours de consultation, etc.)
            model: Modèle LLM à utiliser
            stream: Si True, retourne un générateur pour streaming
            
        Returns:
            Réponse du chatbot
        """
        # Prépare le contexte
        context_str = ""
        if context:
            if "current_product" in context:
                product = context["current_product"]
                context_str = f"\n**Produit en consultation :** {product.get('product_name', 'Inconnu')}"
                context_str += f"\nNutri-Score: {product.get('nutriscore_grade', '?')}"
        
        # Construit l'historique de conversation
        messages = [
            {"role": "system", "content": self.prompts.chatbot_system_prompt()}
        ]
        
        # Ajoute l'historique (derniers 10 messages pour éviter de dépasser le contexte)
        messages.extend(self.conversation_history[-10:])
        
        # Ajoute le message actuel avec contexte
        user_content = user_message
        if context_str:
            user_content += context_str
        
        messages.append({"role": "user", "content": user_content})
        
        try:
            response = self.llm.complete(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=400,
                stream=stream
            )
            
            # Si streaming, on retourne le générateur directement
            if stream:
                return {
                    "success": True,
                    "stream": response,
                    "model_used": model
                }
            
            # Sinon, on met à jour l'historique
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "success": True,
                "response": response,
                "model_used": model,
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
    
    def ask_about_ingredient(
        self,
        ingredient: str,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Pose une question spécifique sur un ingrédient.
        
        Args:
            ingredient: Nom de l'ingrédient
            model: Modèle LLM à utiliser
            
        Returns:
            Explication de l'ingrédient
        """
        question = f"Peux-tu m'expliquer ce qu'est {ingredient} et s'il faut l'éviter ?"
        return self.chat(question, model=model)
    
    def ask_about_allergen(
        self,
        allergen: str,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Pose une question sur un allergène.
        
        Args:
            allergen: Nom de l'allergène
            model: Modèle LLM à utiliser
            
        Returns:
            Informations sur l'allergène
        """
        question = f"Je suis allergique au {allergen}. Quels produits dois-je éviter et quelles sont les alternatives ?"
        return self.chat(question, model=model)
    
    def get_quick_answer(
        self,
        question: str,
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """
        Obtient une réponse rapide sans historique.
        
        Args:
            question: Question de l'utilisateur
            model: Modèle LLM à utiliser
            
        Returns:
            Réponse textuelle
        """
        messages = [
            {"role": "system", "content": self.prompts.chatbot_system_prompt()},
            {"role": "user", "content": question}
        ]
        
        try:
            response = self.llm.complete(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=200
            )
            return response
        except Exception as e:
            return f"Désolé, une erreur s'est produite : {str(e)}"
    
    def suggest_questions(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Suggère des questions pertinentes selon le contexte.
        
        Args:
            context: Contexte actuel (produit consulté, etc.)
            
        Returns:
            Liste de questions suggérées
        """
        base_questions = [
            "🍎 C'est quoi le Nutri-Score exactement ?",
            "🔬 Qu'est-ce qu'un additif alimentaire ?",
            "🥗 Comment composer un repas équilibré ?",
            "⚠️ Quels sont les allergènes les plus courants ?",
            "🏷️ C'est quoi un produit bio ?"
        ]
        
        # Ajoute des questions contextuelles si un produit est consulté
        if context and "current_product" in context:
            product = context["current_product"]
            
            contextual_questions = []
            
            # Questions sur le Nutri-Score
            nutriscore = product.get("nutriscore_grade", "").upper()
            if nutriscore:
                contextual_questions.append(
                    f"Pourquoi ce produit a un Nutri-Score {nutriscore} ?"
                )
            
            # Questions sur les additifs
            additives = product.get("additives_tags", [])
            if additives:
                contextual_questions.append(
                    "Les additifs de ce produit sont-ils dangereux ?"
                )
            
            # Questions sur les allergènes
            allergens = product.get("allergens_tags", [])
            if allergens:
                contextual_questions.append(
                    "Quels sont les allergènes présents dans ce produit ?"
                )
            
            # Questions sur le NOVA
            nova = product.get("nova_group")
            if nova:
                contextual_questions.append(
                    f"C'est grave si un produit est NOVA {nova} ?"
                )
            
            return contextual_questions + base_questions
        
        return base_questions
    
    def explain_score(
        self,
        score_type: str,
        score_value: Any,
        product_name: str = "",
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Explique un score nutritionnel spécifique.
        
        Args:
            score_type: Type de score (nutriscore, nova, etc.)
            score_value: Valeur du score
            product_name: Nom du produit (optionnel)
            model: Modèle LLM à utiliser
            
        Returns:
            Explication du score
        """
        product_str = f" pour {product_name}" if product_name else ""
        
        question = f"Peux-tu m'expliquer en détail le score {score_type.upper()} {score_value}{product_str} ?"
        
        return self.chat(question, model=model)