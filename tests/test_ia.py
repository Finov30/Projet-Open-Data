import pytest
from unittest.mock import Mock, patch

from src.ia import (
    LLMManager,
    ProductAnalyzer,
    NutritionChatbot,
    NutritionPrompts
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_product():
    return {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "nutriscore_grade": "e",
        "nova_group": 4,
        "nutriments": {
            "energy_100g": 539,
            "sugars_100g": 56.3,
            "fat_100g": 30.9,
            "salt_100g": 0.107
        },
        "additives_tags": ["en:e322", "en:e476"]
    }


@pytest.fixture
def mock_llm_response():
    return "Analyse nutritionnelle générée par IA."


# ============================================================================
# TESTS : NutritionPrompts
# ============================================================================

class TestNutritionPrompts:

    def test_product_analysis_system_prompt(self):
        prompt = NutritionPrompts.product_analysis_system_prompt()
        assert isinstance(prompt, str)
        assert "nutritionniste" in prompt.lower()

    def test_product_analysis_user_prompt(self, sample_product):
        prompt = NutritionPrompts.product_analysis_user_prompt(sample_product)
        assert "Nutella" in prompt
        assert "Nutri-Score" in prompt
        assert "NOVA" in prompt

    def test_chatbot_system_prompt(self):
        prompt = NutritionPrompts.chatbot_system_prompt()
        assert isinstance(prompt, str)
        assert "assistant nutrition" in prompt.lower()


# ============================================================================
# TESTS : LLMManager
# ============================================================================

class TestLLMManager:

    def test_initialization(self):
        llm = LLMManager()
        assert llm is not None

    @patch("src.ia.llm_manager.litellm.completion")
    def test_complete_with_fallback(self, mock_completion, mock_llm_response):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_llm_response

        mock_completion.return_value = mock_response

        llm = LLMManager()

        response, model_used = llm.complete_with_fallback(
            messages=[{"role": "user", "content": "Test"}],
            models=["gpt-3.5-turbo"]
        )

        assert response == mock_llm_response
        assert model_used == "gpt-3.5-turbo"


# ============================================================================
# TESTS : ProductAnalyzer
# ============================================================================

class TestProductAnalyzer:

    def test_initialization(self):
        analyzer = ProductAnalyzer()
        assert analyzer.llm is not None
        assert analyzer.prompts is not None

    @patch.object(LLMManager, "complete_with_fallback")
    def test_analyze_success(self, mock_complete, sample_product, mock_llm_response):
        mock_complete.return_value = (mock_llm_response, "gpt-3.5-turbo")

        analyzer = ProductAnalyzer()
        result = analyzer.analyze(sample_product)

        assert result["success"] is True
        assert result["analysis"] == mock_llm_response
        assert result["product_name"] == "Nutella"
        assert result["nutriscore"] == "e"
        assert result["nova_group"] == 4

    @patch.object(LLMManager, "complete_with_fallback")
    def test_analyze_failure(self, mock_complete, sample_product):
        mock_complete.side_effect = Exception("Erreur IA")

        analyzer = ProductAnalyzer()
        result = analyzer.analyze(sample_product)

        assert result["success"] is False
        assert "Erreur IA" in result["error"]

    def test_quick_summary(self, sample_product):
        analyzer = ProductAnalyzer()
        summary = analyzer.quick_summary(sample_product)

        assert "Nutella" in summary
        assert "Nutri-Score E" in summary
        assert "NOVA 4" in summary


# ============================================================================
# TESTS : NutritionChatbot
# ============================================================================

class TestNutritionChatbot:

    def test_initialization(self):
        chatbot = NutritionChatbot()
        assert chatbot.llm is not None
        assert chatbot.prompts is not None
        assert chatbot.conversation_history == []

    @patch.object(LLMManager, "complete")
    def test_chat_success(self, mock_complete, mock_llm_response):
        mock_complete.return_value = mock_llm_response

        chatbot = NutritionChatbot()
        result = chatbot.chat("C'est quoi le Nutri-Score ?")

        assert result["success"] is True
        assert result["response"] == mock_llm_response
        assert len(chatbot.conversation_history) == 2

    def test_clear_history(self):
        chatbot = NutritionChatbot()
        chatbot.conversation_history = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Réponse"}
        ]

        chatbot.clear_history()
        assert chatbot.conversation_history == []

    def test_suggest_questions(self):
        chatbot = NutritionChatbot()
        questions = chatbot.suggest_questions()

        assert isinstance(questions, list)
        assert len(questions) >= 5
        assert all(isinstance(q, str) for q in questions)
