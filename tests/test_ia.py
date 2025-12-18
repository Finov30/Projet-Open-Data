"""
Tests unitaires pour le module IA de NutriScan.

Pour exécuter :
    pytest tests/test_ia.py
    pytest tests/test_ia.py -v  (mode verbose)
    pytest tests/test_ia.py --cov=src.ia  (avec couverture)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ia import (
    LLMManager,
    ProductAnalyzer,
    ProductRecommender,
    NutritionChatbot,
    NutritionPrompts
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_product():
    """Fixture : Données d'un produit exemple."""
    return {
        "code": "3017620422003",
        "product_name": "Nutella",
        "nutriscore_grade": "e",
        "nova_group": 4,
        "energy_100g": 539,
        "sugars_100g": 56.3,
        "fat_100g": 30.9,
        "salt_100g": 0.107,
        "additives_tags": ["en:e322", "en:e476"],
        "categories_tags": ["en:spreads", "en:chocolate-spreads"],
        "labels_tags": []
    }


@pytest.fixture
def sample_alternative():
    """Fixture : Produit alternatif."""
    return {
        "code": "8000300166941",
        "product_name": "Nocciolata Bio",
        "nutriscore_grade": "d",
        "nova_group": 3,
        "energy_100g": 545,
        "sugars_100g": 50,
        "fat_100g": 32,
        "salt_100g": 0.05,
        "categories_tags": ["en:spreads", "en:chocolate-spreads"],
        "labels_tags": ["en:organic"]
    }


@pytest.fixture
def mock_llm_response():
    """Fixture : Réponse mockée d'un LLM."""
    return "Ceci est une analyse nutritionnelle du produit. Le Nutri-Score E indique..."


# ============================================================================
# TESTS : LLMManager
# ============================================================================

class TestLLMManager:
    """Tests pour la classe LLMManager."""
    
    def test_initialization(self):
        """Test l'initialisation du gestionnaire."""
        llm = LLMManager()
        assert llm.default_model == "gpt-3.5-turbo"
        
        llm_custom = LLMManager(default_model="gpt-4")
        assert llm_custom.default_model == "gpt-4"
    
    def test_get_available_models(self):
        """Test la récupération des modèles disponibles."""
        models = LLMManager.get_available_models()
        
        assert isinstance(models, dict)
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert "claude-3-sonnet" in models
        assert "mistral-medium" in models
        
        # Vérifier la structure des données
        for model_name, model_info in models.items():
            assert "provider" in model_info
            assert "cost_per_token" in model_info
            assert "description" in model_info
    
    @patch('litellm.completion')
    def test_complete_success(self, mock_completion, mock_llm_response):
        """Test un appel réussi au LLM."""
        # Mock de la réponse LiteLLM
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_llm_response
        mock_completion.return_value = mock_response
        
        llm = LLMManager()
        messages = [{"role": "user", "content": "Test"}]
        
        response = llm.complete(messages)
        
        assert response == mock_llm_response
        mock_completion.assert_called_once()
    
    @patch('litellm.completion')
    def test_complete_with_custom_params(self, mock_completion, mock_llm_response):
        """Test un appel avec paramètres personnalisés."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_llm_response
        mock_completion.return_value = mock_response
        
        llm = LLMManager()
        messages = [{"role": "user", "content": "Test"}]
        
        response = llm.complete(
            messages,
            model="gpt-4",
            temperature=0.5,
            max_tokens=500
        )
        
        assert response == mock_llm_response
        assert mock_completion.called
    
    @patch('litellm.completion')
    def test_complete_with_fallback(self, mock_completion, mock_llm_response):
        """Test le système de fallback."""
        # Premier modèle échoue, deuxième réussit
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_llm_response
        
        mock_completion.side_effect = [
            Exception("Premier modèle échoué"),
            mock_response
        ]
        
        llm = LLMManager()
        messages = [{"role": "user", "content": "Test"}]
        
        response, model_used = llm.complete_with_fallback(
            messages,
            models=["gpt-4", "gpt-3.5-turbo"]
        )
        
        assert response == mock_llm_response
        assert model_used == "gpt-3.5-turbo"
        assert mock_completion.call_count == 2


# ============================================================================
# TESTS : ProductAnalyzer
# ============================================================================

class TestProductAnalyzer:
    """Tests pour la classe ProductAnalyzer."""
    
    def test_initialization(self):
        """Test l'initialisation de l'analyseur."""
        analyzer = ProductAnalyzer()
        assert analyzer.llm is not None
        assert analyzer.prompts is not None
    
    def test_calculate_health_scores(self, sample_product):
        """Test le calcul des scores de santé."""
        analyzer = ProductAnalyzer()
        scores = analyzer._calculate_health_scores(sample_product)
        
        assert isinstance(scores, dict)
        assert "overall_health" in scores
        assert "processing_level" in scores
        assert "sugar_level" in scores
        assert "fat_quality" in scores
        assert "salt_level" in scores
        
        # Nutri-Score E = 20 points
        assert scores["overall_health"] == 20
        
        # NOVA 4 = niveau de transformation élevé
        assert scores["processing_level"] == 25
        
        # 56.3g de sucres = niveau élevé
        assert scores["sugar_level"] == "high"
    
    @patch.object(LLMManager, 'complete')
    def test_analyze_product_success(self, mock_complete, sample_product, mock_llm_response):
        """Test l'analyse réussie d'un produit."""
        mock_complete.return_value = mock_llm_response
        
        analyzer = ProductAnalyzer()
        result = analyzer.analyze_product(sample_product)
        
        assert result["success"] is True
        assert "analysis" in result
        assert result["analysis"] == mock_llm_response
        assert "scores" in result
        assert result["product_name"] == "Nutella"
        assert "model_used" in result
    
    @patch.object(LLMManager, 'complete')
    def test_analyze_product_failure(self, mock_complete, sample_product):
        """Test la gestion d'erreur lors de l'analyse."""
        mock_complete.side_effect = Exception("API Error")
        
        analyzer = ProductAnalyzer()
        result = analyzer.analyze_product(sample_product)
        
        assert result["success"] is False
        assert "error" in result
        assert "API Error" in result["error"]
    
    @patch.object(LLMManager, 'complete')
    def test_compare_products(self, mock_complete, sample_product, sample_alternative, mock_llm_response):
        """Test la comparaison de produits."""
        mock_complete.return_value = mock_llm_response
        
        analyzer = ProductAnalyzer()
        result = analyzer.compare_products([sample_product, sample_alternative])
        
        assert result["success"] is True
        assert "comparison" in result
        assert "products_scores" in result
        assert len(result["products_scores"]) == 2


# ============================================================================
# TESTS : ProductRecommender
# ============================================================================

class TestProductRecommender:
    """Tests pour la classe ProductRecommender."""
    
    def test_initialization(self):
        """Test l'initialisation du recommandeur."""
        recommender = ProductRecommender()
        assert recommender.llm is not None
        assert recommender.prompts is not None
    
    def test_filter_by_preferences_vegan(self, sample_product, sample_alternative):
        """Test le filtrage par régime végan."""
        recommender = ProductRecommender()
        
        products = [sample_product, sample_alternative]
        preferences = {"diet": "vegan"}
        
        filtered = recommender._filter_by_preferences(products, preferences)
        
        # Les produits sans label vegan sont filtrés
        assert isinstance(filtered, list)
    
    def test_filter_by_preferences_bio(self, sample_product, sample_alternative):
        """Test le filtrage avec préférence bio."""
        recommender = ProductRecommender()
        
        products = [sample_product, sample_alternative]
        preferences = {"prefer_bio": True}
        
        filtered = recommender._filter_by_preferences(products, preferences)
        
        # Le produit bio doit être en premier
        assert filtered[0]["product_name"] == "Nocciolata Bio"
    
    def test_rank_alternatives(self, sample_product, sample_alternative):
        """Test le classement des alternatives."""
        recommender = ProductRecommender()
        
        alternatives = [sample_product, sample_alternative]
        ranked = recommender._rank_alternatives(sample_product, alternatives)
        
        assert len(ranked) == 2
        assert all("health_score" in alt for alt in ranked)
        
        # Le produit avec meilleur score devrait être premier
        assert ranked[0]["health_score"] >= ranked[1]["health_score"]
    
    @patch.object(LLMManager, 'complete')
    def test_recommend_alternatives_success(self, mock_complete, sample_product, sample_alternative, mock_llm_response):
        """Test les recommandations réussies."""
        mock_complete.return_value = mock_llm_response
        
        recommender = ProductRecommender()
        result = recommender.recommend_alternatives(
            current_product=sample_product,
            alternatives=[sample_alternative]
        )
        
        assert result["success"] is True
        assert "recommendation" in result
        assert "top_alternatives" in result
        assert len(result["top_alternatives"]) <= 5


# ============================================================================
# TESTS : NutritionChatbot
# ============================================================================

class TestNutritionChatbot:
    """Tests pour la classe NutritionChatbot."""
    
    def test_initialization(self):
        """Test l'initialisation du chatbot."""
        chatbot = NutritionChatbot()
        assert chatbot.llm is not None
        assert chatbot.prompts is not None
        assert chatbot.conversation_history == []
    
    @patch.object(LLMManager, 'complete')
    def test_chat_success(self, mock_complete, mock_llm_response):
        """Test une conversation réussie."""
        mock_complete.return_value = mock_llm_response
        
        chatbot = NutritionChatbot()
        result = chatbot.chat("C'est quoi le Nutri-Score ?")
        
        assert result["success"] is True
        assert "response" in result
        assert result["response"] == mock_llm_response
        
        # Vérifier que l'historique est mis à jour
        assert len(chatbot.conversation_history) == 2
    
    @patch.object(LLMManager, 'complete')
    def test_chat_with_context(self, mock_complete, sample_product, mock_llm_response):
        """Test une conversation avec contexte."""
        mock_complete.return_value = mock_llm_response
        
        chatbot = NutritionChatbot()
        context = {"current_product": sample_product}
        
        result = chatbot.chat("Analyse ce produit", context=context)
        
        assert result["success"] is True
        assert "response" in result
    
    def test_clear_history(self):
        """Test l'effacement de l'historique."""
        chatbot = NutritionChatbot()
        chatbot.conversation_history = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Réponse"}
        ]
        
        chatbot.clear_history()
        assert chatbot.conversation_history == []
    
    def test_suggest_questions_without_context(self):
        """Test les suggestions sans contexte."""
        chatbot = NutritionChatbot()
        questions = chatbot.suggest_questions()
        
        assert isinstance(questions, list)
        assert len(questions) >= 5
        assert all(isinstance(q, str) for q in questions)
    
    def test_suggest_questions_with_context(self, sample_product):
        """Test les suggestions avec contexte produit."""
        chatbot = NutritionChatbot()
        context = {"current_product": sample_product}
        
        questions = chatbot.suggest_questions(context)
        
        assert isinstance(questions, list)
        assert len(questions) >= 5
        
        # Devrait contenir des questions contextuelles
        assert any("Nutri-Score E" in q for q in questions)


# ============================================================================
# TESTS : NutritionPrompts
# ============================================================================

class TestNutritionPrompts:
    """Tests pour la classe NutritionPrompts."""
    
    def test_analyze_product_prompt(self, sample_product):
        """Test la génération du prompt d'analyse."""
        prompts = NutritionPrompts()
        prompt = prompts.analyze_product(sample_product)
        
        assert isinstance(prompt, str)
        assert "Nutella" in prompt
        assert "Nutri-Score" in prompt
        assert "NOVA" in prompt
    
    def test_recommend_alternatives_prompt(self, sample_product, sample_alternative):
        """Test la génération du prompt de recommandation."""
        prompts = NutritionPrompts()
        prompt = prompts.recommend_alternatives(
            sample_product,
            [sample_alternative],
            {"diet": "vegan"}
        )
        
        assert isinstance(prompt, str)
        assert "alternative" in prompt.lower()
        assert "vegan" in prompt.lower()
    
    def test_chatbot_system_prompt(self):
        """Test le prompt système du chatbot."""
        prompts = NutritionPrompts()
        prompt = prompts.chatbot_system_prompt()
        
        assert isinstance(prompt, str)
        assert "nutrition" in prompt.lower()
        assert len(prompt) > 100


# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

class TestIntegration:
    """Tests d'intégration du module."""
    
    @pytest.mark.integration
    @patch.object(LLMManager, 'complete')
    def test_full_workflow(self, mock_complete, sample_product, sample_alternative, mock_llm_response):
        """Test un workflow complet : analyse + recommandation + chat."""
        mock_complete.return_value = mock_llm_response
        
        # 1. Analyse
        analyzer = ProductAnalyzer()
        analysis = analyzer.analyze_product(sample_product)
        assert analysis["success"] is True
        
        # 2. Recommandation
        recommender = ProductRecommender()
        recommendations = recommender.recommend_alternatives(
            sample_product,
            [sample_alternative]
        )
        assert recommendations["success"] is True
        
        # 3. Chat
        chatbot = NutritionChatbot()
        chat_response = chatbot.chat("Explique l'analyse")
        assert chat_response["success"] is True


# ============================================================================
# CONFIGURATION PYTEST
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.ia", "--cov-report=html"])