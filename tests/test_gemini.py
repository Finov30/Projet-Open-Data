# -*- coding: utf-8 -*-
"""
Test de configuration Gemini pour NutriScan.
Exécutez ce fichier pour vérifier que votre environnement IA fonctionne.
"""

import os
import sys
from dotenv import load_dotenv


# ---------------------------------------------------------------------
# TEST 1 : Chargement du fichier .env
# ---------------------------------------------------------------------
def test_env_loading():
    print("=" * 60)
    print("TEST 1 : Chargement du fichier .env")
    print("=" * 60)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("[FAIL] GEMINI_API_KEY introuvable")
        print("Vérifiez que le fichier .env contient : GEMINI_API_KEY=...")
        return False

    if not api_key.startswith("AIza"):
        print("[WARN] Le format de la clé semble incorrect")
        print(f"Préfixe actuel : {api_key[:10]}...")
        return False

    print("[OK] Clé API Gemini chargée")
    print(f"Préfixe : {api_key[:10]}...")
    return True


# ---------------------------------------------------------------------
# TEST 2 : Import LiteLLM
# ---------------------------------------------------------------------
def test_litellm_import():
    print("\n" + "=" * 60)
    print("TEST 2 : Import de LiteLLM")
    print("=" * 60)

    try:
        import litellm
        print(f"[OK] LiteLLM importé (version {litellm.__version__})")
        return True
    except ImportError:
        print("[FAIL] LiteLLM non installé")
        print("Installez avec : uv add litellm google-generativeai")
        return False


# ---------------------------------------------------------------------
# TEST 3 : Connexion Gemini via LiteLLM
# ---------------------------------------------------------------------
def test_gemini_connection():
    print("\n" + "=" * 60)
    print("TEST 3 : Connexion à Gemini")
    print("=" * 60)

    try:
        import litellm

        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": "Réponds uniquement par OK"}],
            max_tokens=10
        )

        text = response.choices[0].message.content
        print("[OK] Gemini répond correctement")
        print(f"Réponse : {text}")
        return True

    except Exception as e:
        print("[FAIL] Erreur de connexion Gemini")
        print(f"Erreur : {e}")
        return False


# ---------------------------------------------------------------------
# TEST 4 : Module IA NutriScan
# ---------------------------------------------------------------------
def test_module_ia():
    print("\n" + "=" * 60)
    print("TEST 4 : Module IA NutriScan")
    print("=" * 60)

    try:
        from src.ia import LLMManager, ProductAnalyzer
        print("[OK] Import des modules IA réussi")

        llm = LLMManager()

        # Test LLMManager
        response = llm.complete(
            messages=[{"role": "user", "content": "Dis bonjour"}],
            model="gemini/gemini-1.5-flash",
            max_tokens=20
        )
        print("[OK] LLMManager fonctionne")
        print(f"Réponse : {response}")

        # Test ProductAnalyzer
        analyzer = ProductAnalyzer(llm)

        test_product = {
            "product_name": "Produit Test",
            "brands": "NutriScan",
            "nutriscore_grade": "a",
            "nova_group": 1,
            "nutriments": {
                "energy_100g": 200,
                "sugars_100g": 5,
                "fat_100g": 3,
                "salt_100g": 0.1
            }
        }

        result = analyzer.analyze(
            product=test_product,
            model="gemini/gemini-1.5-flash"
        )

        if not result.get("success"):
            print("[FAIL] ProductAnalyzer a échoué")
            print(result.get("error"))
            return False

        print("[OK] ProductAnalyzer fonctionne")
        print(f"Analyse générée ({len(result['analysis'])} caractères)")
        return True

    except Exception as e:
        print("[FAIL] Erreur dans le module IA")
        print(f"Erreur : {e}")
        return False


# ---------------------------------------------------------------------
# TEST 5 : Modèles disponibles
# ---------------------------------------------------------------------
def test_models_availability():
    print("\n" + "=" * 60)
    print("TEST 5 : Modèles configurés")
    print("=" * 60)

    try:
        from src.ia import LLMManager

        models = LLMManager.get_available_models()

        print(f"[OK] {len(models)} modèles configurés :\n")
        for name, info in models.items():
            print(f"- {name}")
            print(f"  Provider : {info['provider']}")
            print(f"  Description : {info['description']}")
            print()

        return True

    except Exception as e:
        print("[FAIL] Impossible de récupérer les modèles")
        print(e)
        return False


# ---------------------------------------------------------------------
# LANCEUR GLOBAL
# ---------------------------------------------------------------------
def run_all_tests():
    print("\n" + "=" * 60)
    print("TEST DE CONFIGURATION GEMINI - NUTRISCAN")
    print("=" * 60)

    tests = [
        test_env_loading,
        test_litellm_import,
        test_gemini_connection,
        test_module_ia,
        test_models_availability,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Résultat : {passed}/{total} tests réussis")

    if passed == total:
        print("\n[SUCCÈS] Configuration Gemini valide")
        return 0
    else:
        print("\n[ERREUR] Certains tests ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
