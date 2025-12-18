"""
Module IA pour NutriScan - Analyse nutritionnelle intelligente.

Ce module fournit des fonctionnalités d'analyse alimentaire basées sur l'IA :
- Analyse de produits avec LLMs
- Système de recommandation d'alternatives
- Chatbot conversationnel
- Comparaison de produits

Auteurs : [Votre équipe]
Date : Décembre 2024
"""

from .llm_manager import LLMManager
from .product_analyzer import ProductAnalyzer
from .recommender import ProductRecommender
from .chatbot import NutritionChatbot
from .prompts import NutritionPrompts

__version__ = "1.0.0"
__all__ = [
    "LLMManager",
    "ProductAnalyzer",
    "ProductRecommender", 
    "NutritionChatbot",
    "NutritionPrompts"
]

# Configuration par défaut
DEFAULT_MODEL = "gpt-3.5-turbo"
FALLBACK_MODELS = ["gpt-3.5-turbo", "mistral-medium", "claude-3-sonnet"]