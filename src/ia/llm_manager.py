"""
Gestionnaire centralisé pour les appels LiteLLM avec support multi-modèles.
"""
import os
from typing import Dict, List, Optional, Any
import litellm
from dotenv import load_dotenv

load_dotenv()

class LLMManager:
    """Gestionnaire pour les appels aux modèles de langage via LiteLLM."""
    
    # Configuration des modèles disponibles
    MODELS = {
        "gpt-4": {
            "provider": "openai",
            "cost_per_token": 0.00003,
            "description": "Modèle le plus performant pour analyses complexes"
        },
        "gpt-3.5-turbo": {
            "provider": "openai", 
            "cost_per_token": 0.000002,
            "description": "Modèle rapide et économique pour tâches simples"
        },
        "claude-3-sonnet": {
            "provider": "anthropic",
            "cost_per_token": 0.000015,
            "description": "Excellent pour analyses nuancées"
        },
        "mistral-medium": {
            "provider": "mistral",
            "cost_per_token": 0.0000027,
            "description": "Alternative open-source performante"
        },
        
        "gemini-1.5-flash": {
            "provider": "gemini",
            "cost_per_token": 0.0000005,
            "description": "Rapide et économique (Google Gemini)"
        },
          
        "gemini-2.5-flash-lite": {
            "provider": "gemini",
            "cost_per_token": 0.000001,
            "description": "Analyse avancée (Google Gemini)"
    },


    }
    
    def __init__(self, default_model: str = "gemini/gemini-1.5-flash"):
        """
        Initialise le gestionnaire LLM.
        
        Args:
            default_model: Modèle par défaut à utiliser
        """
        self.default_model = default_model
        self._setup_api_keys()
        
    def _setup_api_keys(self):
        """Configure les clés API depuis les variables d'environnement."""
        # Les clés sont automatiquement lues par LiteLLM depuis l'environnement
        # OPENAI_API_KEY, ANTHROPIC_API_KEY, MISTRAL_API_KEY
        pass
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        Effectue un appel de complétion au modèle.
        
        Args:
            messages: Liste des messages au format [{"role": "user", "content": "..."}]
            model: Modèle à utiliser (utilise default_model si None)
            temperature: Température de génération (0-1)
            max_tokens: Nombre maximum de tokens
            stream: Si True, retourne un générateur de streaming
            **kwargs: Arguments supplémentaires pour LiteLLM
            
        Returns:
            Réponse du modèle sous forme de texte
        """
        model = model or self.default_model
        
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            if stream:
                return response  # Retourne le générateur pour streaming
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel au modèle {model}: {str(e)}")
    
    def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        models: Optional[List[str]] = None,
        **kwargs
    ) -> tuple[str, str]:
        """
        Essaie plusieurs modèles en cas d'échec (fallback).
        
        Args:
            messages: Messages à envoyer
            models: Liste des modèles à essayer (ordre de priorité)
            **kwargs: Arguments supplémentaires
            
        Returns:
            Tuple (réponse, modèle_utilisé)
        """
        if models is None:
            models = [ "gemini/gemini-2.5-flash-lite","ollama/llama3.2"
                ]
        
        last_error = None
        for model in models:
            try:
                response = self.complete(messages=messages, model=model, **kwargs)
                return response, model
            except Exception as e:
                last_error = e
                continue
        
        raise Exception(f"Tous les modèles ont échoué. Dernière erreur: {last_error}")
    
    def get_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Génère un embedding pour un texte.
        
        Args:
            text: Texte à encoder
            model: Modèle d'embedding à utiliser
            
        Returns:
            Vecteur d'embedding
        """
        try:
            response = litellm.embedding(model=model, input=text)
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Erreur lors de la génération d'embedding: {str(e)}")
    
    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des modèles configurés."""
        return LLMManager.MODELS
    
    def estimate_cost(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> float:
        """
        Estime le coût d'un appel (approximatif).
        
        Args:
            messages: Messages à envoyer
            model: Modèle à utiliser
            
        Returns:
            Coût estimé en dollars
        """
        model = model or self.default_model
        if model not in self.MODELS:
            return 0.0
        
        # Estimation grossière: 1 token ≈ 4 caractères
        total_chars = sum(len(m.get("content", "")) for m in messages)
        estimated_tokens = total_chars / 4
        
        cost_per_token = self.MODELS[model]["cost_per_token"]
        return estimated_tokens * cost_per_token