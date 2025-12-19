"""
Gestionnaire centralisé pour les appels LiteLLM avec fallback intelligent.
"""
import os
from typing import Dict, List, Optional, Any
import litellm
from dotenv import load_dotenv

load_dotenv()


class LLMManager:
    """Gestionnaire pour les appels aux modèles de langage via LiteLLM."""

    MODELS = {
        "ollama/mistral": {
            "provider": "ollama",
            "description": "Modèle local via Ollama (sans clé API)"
        },
        "gemini/gemini-2.5-flash-lite": {
            "provider": "gemini",
            "description": "Google Gemini (clé requise)"
        },
        "openai/gpt-3.5-turbo": {
            "provider": "openai",
            "description": "OpenAI GPT-3.5 (clé requise)"
        },
    }

    def __init__(self):
        self.default_model = self._detect_best_model()

    # --------------------------------------------------
    # Détection intelligente du modèle
    # --------------------------------------------------
    def _detect_best_model(self) -> str:
        # 1️⃣ Ollama (local, recommandé)
        if self._ollama_available():
            return "ollama/mistral"

        # 2️⃣ Gemini
        if os.getenv("GEMINI_API_KEY"):
            return "gemini/gemini-2.5-flash-lite"

        # 3️⃣ OpenAI
        if os.getenv("OPENAI_API_KEY"):
            return "openai/gpt-3.5-turbo"

        raise RuntimeError(
            "Aucun modèle IA disponible.\n"
            "➡️ Installe Ollama OU définis GEMINI_API_KEY / OPENAI_API_KEY."
        )

    def _ollama_available(self) -> bool:
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=1)
            return r.status_code == 200
        except Exception:
            return False

    # --------------------------------------------------
    # Appel principal
    # --------------------------------------------------
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> str:
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
                return response

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(
                f"Erreur lors de l'appel au modèle {model} : {str(e)}"
            )

    # --------------------------------------------------
    # Fallback multi-modèles
    # --------------------------------------------------
    def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        models: Optional[List[str]] = None,
        **kwargs
    ) -> tuple[str, str]:

        models = models or [
            "ollama/mistral",
            "gemini/gemini-2.5-flash-lite",
            "openai/gpt-3.5-turbo",
        ]

        last_error = None

        for model in models:
            try:
                response = self.complete(
                    messages=messages,
                    model=model,
                    **kwargs
                )
                return response, model
            except Exception as e:
                last_error = e
                continue

        raise Exception(f"Tous les modèles ont échoué : {last_error}")

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, Any]]:
        return LLMManager.MODELS
