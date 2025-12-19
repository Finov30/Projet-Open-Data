"""
NutriScan - Pipeline principal

Ce fichier orchestre les différentes étapes du pipeline :
    1. Récupération des données (Sam)
    2. Transformation (Aurélien)
    3. Enrichissement / Stockage (Jules)
    4. Tests automatisés (pytest)
    5. Streamlit IA / Chatbot (Juba)

Usage:
    python pipeline.py
"""

import subprocess
import sys

# ========================================
# CONFIGURATION - Modifier ici la taille des données
# ========================================

# OpenFoodFacts : nombre de produits par catégorie
OPENFOODFACTS_PRODUCTS_PER_CATEGORY = 50

# Liste des catégories à rechercher sur OpenFoodFacts
OPENFOODFACTS_CATEGORIES = [
    "chocolat",
    "yaourt",
    "biscuit",
    "pain",
    "fromage",
    "jus",
    "céréales",
    "pâtes",
    "sauce",
    "boisson",
]

# ========================================


def run_pipeline():
    """Exécute le pipeline complet."""

    # ========================================
    # ÉTAPE 1 : Récupération des données
    # ========================================
    from src.data.fetch_data import (
        fetch_openfoodfacts_products,
        fetch_ciqual_data,
        OUTPUT_DIR,
    )

    print("\n" + "=" * 60)
    print("ÉTAPE 1 : Récupération des données")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # OpenFoodFacts
    print("\n[1/2] OpenFoodFacts")
    print(
        f"      Config: {OPENFOODFACTS_PRODUCTS_PER_CATEGORY} produits "
        f"x {len(OPENFOODFACTS_CATEGORIES)} catégories"
    )

    df_off = fetch_openfoodfacts_products(
        queries=OPENFOODFACTS_CATEGORIES,
        products_per_query=OPENFOODFACTS_PRODUCTS_PER_CATEGORY,
    )

    if not df_off.empty:
        off_file = OUTPUT_DIR / "openfoodfacts_products.csv"
        df_off.to_csv(off_file, index=False, encoding="utf-8")
        print(f"  -> Sauvegardé: {off_file} ({len(df_off)} produits)")

    # CIQUAL
    print("\n[2/2] CIQUAL (ANSES)")
    df_ciqual = fetch_ciqual_data()

    if not df_ciqual.empty:
        ciqual_file = OUTPUT_DIR / "ciqual_aliments.csv"
        df_ciqual.to_csv(ciqual_file, index=False, encoding="utf-8")
        print(f"  -> Sauvegardé: {ciqual_file} ({len(df_ciqual)} aliments)")

    # ========================================
    # ÉTAPE 2 : Transformation
    # ========================================
    print("\n" + "=" * 60)
    print("ÉTAPE 2 : Transformation des données")
    print("=" * 60)

    from utils.transformer import run_transformations

    run_transformations()

    # ========================================
    # ÉTAPE 3 : Enrichissement / Stockage
    # ========================================
    print("\n" + "=" * 60)
    print("ÉTAPE 3 : Enrichissement / Stockage")
    print("=" * 60)

    from src.enricher.enrich_data import main as enrich_data

    enrich_data()

    # ========================================
    # ÉTAPE 4 : Tests automatisés
    # ========================================
    print("\n" + "=" * 60)
    print("ÉTAPE 4 : Exécution des tests")
    print("=" * 60)

    result = subprocess.run(
        ["pytest", "tests", "-v"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    if result.returncode != 0:
        print("\n[ERREUR] Les tests ont échoué ❌")
        print("Arrêt du pipeline avant le lancement de Streamlit.")
        sys.exit(1)

    print("\n[OK] Tous les tests sont passés avec succès ✅")

    # ========================================
    # ÉTAPE 5 : Streamlit IA / Chatbot
    # ========================================
    print("\n" + "=" * 60)
    print("ÉTAPE 5 : Lancement de Streamlit")
    print("=" * 60)

    subprocess.run(["streamlit", "run", "streamlit.py"])

    print("\n" + "=" * 60)
    print("PIPELINE TERMINÉ 🎉")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
