"""
Test de configuration Gemini pour NutriScan.
Exécutez ce fichier pour vérifier que votre clé API fonctionne.
"""

import os
import sys
from dotenv import load_dotenv

def test_env_loading():
    """Test 1 : Vérifier que le fichier .env est chargé."""
    print("=" * 60)
    print("TEST 1 : Chargement du fichier .env")
    print("=" * 60)
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ÉCHEC : La clé GEMINI_API_KEY n'est pas trouvée dans .env")
        print("\nVérifiez que :")
        print("  1. Le fichier .env existe dans le dossier racine")
        print("  2. Il contient : GEMINI_API_KEY=votre_cle")
        print("  3. La clé commence par 'AIzaSy'")
        return False
    
    if not api_key.startswith("AIzaSy"):
        print(f"⚠️  ATTENTION : La clé ne semble pas valide")
        print(f"   Format actuel : {api_key[:10]}...")
        print(f"   Format attendu : AIzaSy...")
        return False
    
    print(f"✅ SUCCÈS : Clé API trouvée")
    print(f"   Préfixe : {api_key[:10]}...")
    print(f"   Longueur : {len(api_key)} caractères")
    return True


def test_litellm_import():
    """Test 2 : Vérifier que LiteLLM est installé."""
    print("\n" + "=" * 60)
    print("TEST 2 : Import de LiteLLM")
    print("=" * 60)
    
    try:
        import litellm
        print(f"✅ SUCCÈS : LiteLLM version {litellm.__version__}")
        return True
    except ImportError:
        print("❌ ÉCHEC : LiteLLM n'est pas installé")
        print("\nInstallez-le avec :")
        print("  uv add litellm google-generativeai")
        print("  # ou")
        print("  pip install litellm google-generativeai")
        return False


def test_gemini_connection():
    """Test 3 : Tester la connexion à l'API Gemini."""
    print("\n" + "=" * 60)
    print("TEST 3 : Connexion à l'API Gemini")
    print("=" * 60)
    
    try:
        import litellm
        
        print("Envoi d'une requête de test à Gemini Flash...")
        
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=[
                {"role": "user", "content": "Réponds simplement 'OK' si tu me reçois"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        
        print(f"✅ SUCCÈS : Connexion établie")
        print(f"   Réponse de Gemini : {result}")
        return True
        
    except Exception as e:
        print(f"❌ ÉCHEC : Erreur de connexion")
        print(f"   Erreur : {str(e)}")
        
        if "API_KEY_INVALID" in str(e):
            print("\n💡 Solution : Votre clé API n'est pas valide")
            print("   1. Allez sur https://aistudio.google.com/app/apikey")
            print("   2. Créez une nouvelle clé")
            print("   3. Mettez à jour votre fichier .env")
        
        elif "quota" in str(e).lower():
            print("\n💡 Solution : Quota dépassé")
            print("   1. Attendez 24h (reset quotidien)")
            print("   2. Ou créez un nouveau projet Google Cloud")
        
        else:
            print("\n💡 Vérifiez votre connexion internet")
        
        return False


def test_module_ia():
    """Test 4 : Tester le module IA de NutriScan."""
    print("\n" + "=" * 60)
    print("TEST 4 : Module IA NutriScan")
    print("=" * 60)
    
    try:
        from src.ia import LLMManager, ProductAnalyzer
        
        print("✅ Import du module IA réussi")
        
        # Test LLMManager
        print("\nTest du LLMManager...")
        llm = LLMManager()
        
        response = llm.complete(
            messages=[{"role": "user", "content": "Dis bonjour"}],
            model="gemini/gemini-1.5-flash",
            max_tokens=20
        )
        
        print(f"✅ LLMManager fonctionne")
        print(f"   Réponse : {response[:50]}...")
        
        # Test ProductAnalyzer
        print("\nTest du ProductAnalyzer...")
        analyzer = ProductAnalyzer(llm)
        
        test_product = {
            "product_name": "Test Product",
            "nutriscore_grade": "a",
            "nova_group": 1,
            "energy_100g": 200,
            "sugars_100g": 5,
            "fat_100g": 3,
            "salt_100g": 0.1
        }
        
        result = analyzer.analyze_product(test_product, model="gemini/gemini-1.5-flash")
        
        if result["success"]:
            print(f"✅ ProductAnalyzer fonctionne")
            print(f"   Analyse générée : {len(result['analysis'])} caractères")
            print(f"   Score calculé : {result['scores']['overall_health']}/100")
        else:
            print(f"⚠️  ProductAnalyzer a retourné une erreur : {result.get('error')}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ ÉCHEC : Impossible d'importer le module IA")
        print(f"   Erreur : {e}")
        print("\n💡 Vérifiez que les fichiers du module IA sont dans src/ia/")
        return False
    
    except Exception as e:
        print(f"❌ ÉCHEC : Erreur lors du test")
        print(f"   Erreur : {e}")
        return False


def test_models_availability():
    """Test 5 : Vérifier les modèles disponibles."""
    print("\n" + "=" * 60)
    print("TEST 5 : Modèles disponibles")
    print("=" * 60)
    
    try:
        from src.ia import LLMManager
        
        models = LLMManager.get_available_models()
        
        print(f"✅ {len(models)} modèles configurés :\n")
        
        for model_name, model_info in models.items():
            icon = "🟢" if "gemini" in model_name else "🔵"
            print(f"{icon} {model_name}")
            print(f"   Provider: {model_info['provider']}")
            print(f"   Description: {model_info['description']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ ÉCHEC : {e}")
        return False


def run_all_tests():
    """Exécute tous les tests dans l'ordre."""
    print("\n")
    print("🧪 " + "=" * 58)
    print("🧪 TEST DE CONFIGURATION GEMINI - NUTRISCAN")
    print("🧪 " + "=" * 58)
    print()
    
    tests = [
        ("Chargement .env", test_env_loading),
        ("Import LiteLLM", test_litellm_import),
        ("Connexion Gemini", test_gemini_connection),
        ("Module IA", test_module_ia),
        ("Modèles disponibles", test_models_availability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Résultat : {passed}/{total} tests réussis")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 FÉLICITATIONS ! Votre configuration est parfaite !")
        print("Vous pouvez maintenant utiliser le module IA avec Gemini.")
        print("\nProchaines étapes :")
        print("  1. Lancez les exemples : python example_usage.py")
        print("  2. Intégrez avec Streamlit")
        print("  3. Committez sur GitHub")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué.")
        print("Consultez les messages d'erreur ci-dessus pour résoudre les problèmes.")
        print("\nAide disponible :")
        print("  - README_IA.md : Documentation complète")
        print("  - Guide Gemini : Instructions détaillées")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)