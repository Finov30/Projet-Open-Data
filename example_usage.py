"""
Exemples d'utilisation du module IA de NutriScan.

Ce fichier montre comment utiliser les différentes fonctionnalités IA.
"""
import time
from src.ia import (
    LLMManager,
    ProductAnalyzer,
    ProductRecommender,
    NutritionChatbot
)

# Exemple de données produit (depuis OpenFoodFacts)
example_product = {
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

alternative_product = {
    "code": "8000300166941",
    "product_name": "Nocciolata",
    "nutriscore_grade": "d",
    "nova_group": 3,
    "energy_100g": 545,
    "sugars_100g": 50,
    "fat_100g": 32,
    "salt_100g": 0.05,
    "categories_tags": ["en:spreads", "en:chocolate-spreads"],
    "labels_tags": ["en:organic"]
}


# def example_1_analyze_product():
#     """Exemple 1 : Analyser un produit."""
#     print("=" * 60)
#     print("EXEMPLE 1 : ANALYSE DE PRODUIT")
#     print("=" * 60)
    
#     # Initialisation
#     analyzer = ProductAnalyzer()
    
#     # Analyse du produit avec Gemini
#     result = analyzer.analyze(
#         product=example_product,
#         model="gemini/gemini-2.5-flash-lite"  # Modèle gratuit et rapide
#     )
    
#     if result["success"]:
#         print(f"\n📊 Analyse de : {result['product_name']}")
#         print(f"\n{result['analysis']}")
#         print(f"\n📈 Scores calculés :")
#         for key, value in result["scores"].items():
#             print(f"  - {key}: {value}")
#         print(f"\n🤖 Modèle utilisé : {result['model_used']}")
#     else:
#         print(f"❌ Erreur : {result['error']}")


# def example_2_compare_products():
#     """Exemple 2 : Comparer des produits."""
#     print("\n" + "=" * 60)
#     print("EXEMPLE 2 : COMPARAISON DE PRODUITS")
#     print("=" * 60)
    
#     analyzer = ProductAnalyzer()
    
#     result = analyzer.compare_products(
#         products=[example_product, alternative_product],
#         model="gemini/gemini-2.5-flash-lite"
#     )
    
#     if result["success"]:
#         print(f"\n{result['comparison']}")
#         print(f"\n📊 Scores des produits :")
#         for item in result["products_scores"]:
#             print(f"\n  {item['product']['product_name']} :")
#             print(f"    Score global : {item['scores']['overall_health']}/100")
#     else:
#         print(f"❌ Erreur : {result['error']}")


# def example_3_recommend_alternatives():
#     """Exemple 3 : Recommander des alternatives."""
#     print("\n" + "=" * 60)
#     print("EXEMPLE 3 : RECOMMANDATION D'ALTERNATIVES")
#     print("=" * 60)
    
#     recommender = ProductRecommender()
    
#     # Préférences utilisateur
#     user_prefs = {
#         "diet": "vegetarian",
#         "prefer_bio": True,
#         "allergens": []
#     }
    
#     result = recommender.recommend_alternatives(
#         current_product=example_product,
#         alternatives=[alternative_product],
#         user_preferences=user_prefs,
#         model="gemini/gemini-2.5-flash-lite"
#     )
    
#     if result["success"]:
#         print(f"\n🔄 Alternatives pour : {result['current_product']}")
#         print(f"\n{result['recommendation']}")
#         print(f"\n📋 Top {len(result['top_alternatives'])} alternatives trouvées")
#     else:
#         print(f"❌ Erreur : {result['error']}")


def example_4_chatbot():
    """Exemple 4 : Utiliser le chatbot."""
    print("\n" + "=" * 60)
    print("EXEMPLE 4 : CHATBOT NUTRITION")
    print("=" * 60)
    
    chatbot = NutritionChatbot()
    
    # Contexte : produit en consultation
    context = {
        "current_product": example_product
    }
    
    # Questions
    questions = [
        "Pourquoi ce produit a un mauvais Nutri-Score ?",
        "C'est quoi le NOVA 4 ?",
        "Quels sont les additifs dangereux ?"
    ]

    for question in questions:
        print(f"\n👤 Question : {question}")
        
        result = chatbot.chat(
            user_message=question,
            context=context,
            model="gemini/gemini-2.5-flash-lite"
        )
        time.sleep(1) 
        if result["success"]:
            print(f"🤖 Réponse : {result['response']}")
        else:
            print(f"❌ Erreur : {result['error']}")


# def example_5_explain_ingredient():
#     """Exemple 5 : Expliquer un ingrédient."""
#     print("\n" + "=" * 60)
#     print("EXEMPLE 5 : EXPLICATION D'INGRÉDIENT")
#     print("=" * 60)
    
#     analyzer = ProductAnalyzer()
    
#     result = analyzer.explain_ingredient(
#         ingredient="E476 (polyglycerol polyricinoleate)",
#         context="Dans une pâte à tartiner au chocolat",
#         model="gemini/gemini-2.5-flash-lite"
#     )
    
#     if result["success"]:
#         print(f"\n🔬 Ingrédient : {result['ingredient']}")
#         print(f"\n{result['explanation']}")
#     else:
#         print(f"❌ Erreur : {result['error']}")


def example_6_model_comparison():
    """Exemple 6 : Comparer différents modèles."""
    print("\n" + "=" * 60)
    print("EXEMPLE 6 : COMPARAISON DE MODÈLES")
    print("=" * 60)
    
    llm = LLMManager()
    analyzer = ProductAnalyzer(llm)
    
    models_to_test = ["gemini/gemini-2.5-flash-lite", "ollama/llama3.2"]
    
    for model in models_to_test:
        time.sleep(1)
        print(f"\n🤖 Test avec {model}...")
        
        try:
            result = analyzer.analyze(
                product_data=example_product,
                model=model
            )
            
            if result["success"]:
                print(f"✅ Succès avec {model}")
                print(f"Longueur de l'analyse : {len(result['analysis'])} caractères")
            else:
                print(f"❌ Échec avec {model}: {result['error']}")
                
        except Exception as e:
            print(f"❌ Erreur avec {model}: {str(e)}")


def example_7_streaming_chatbot():
    """Exemple 7 : Chatbot avec streaming."""
    print("\n" + "=" * 60)
    print("EXEMPLE 7 : CHATBOT AVEC STREAMING")
    print("=" * 60)
    
    chatbot = NutritionChatbot()
    
    question = "Explique-moi en détail ce qu'est le Nutri-Score et comment il est calculé."
    
    print(f"\n👤 Question : {question}")
    print("🤖 Réponse (streaming) : ", end="", flush=True)
    
    result = chatbot.chat(
        user_message=question,
        model="gemini/gemini-1.5-flash",
        stream=True
    )
    
    if result["success"]:
        for chunk in result["stream"]:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    print(delta.content, end="", flush=True)
        print("\n")
    else:
        print(f"\n❌ Erreur : {result['error']}")


if __name__ == "__main__":
    print("\n🥗 NUTRISCAN - EXEMPLES D'UTILISATION DU MODULE IA\n")
    
    # Exécute tous les exemples
    try:
        # example_1_analyze_product()
        # example_2_compare_products()
        # example_3_recommend_alternatives()
        example_4_chatbot()
        # example_5_explain_ingredient()
        
        # Exemples avancés (peuvent nécessiter des clés API supplémentaires)
        example_6_model_comparison()
        example_7_streaming_chatbot()
        
        print("\n" + "=" * 60)
        print("✅ Tous les exemples ont été exécutés avec succès !")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution : {str(e)}")
        print("\nAssurez-vous d'avoir :")
        print("  1. Installé toutes les dépendances (uv sync)")
        print("  2. Configuré vos clés API dans le fichier .env")
        print("  3. Accès internet pour les appels API")