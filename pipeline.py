"""
NutriScan - Pipeline principal

Ce fichier orchestre les différentes étapes du pipeline :
    1. Récupération des données (Sam)
    2. Transformation (Aurélien)
    3. Enrichissement/Stockage (Jules)
    4. Streamlit IA/Chatbot (Juba)

Usage:
    python pipeline.py
"""

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
    # ÉTAPE 1 : Récupération des données (Sam)
    # ========================================
    from src.data.fetch_data import fetch_openfoodfacts_products, fetch_ciqual_data, OUTPUT_DIR

    print("\n" + "=" * 60)
    print("ÉTAPE 1 : Récupération des données")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # OpenFoodFacts
    print("\n[1/2] OpenFoodFacts")
    print(f"      Config: {OPENFOODFACTS_PRODUCTS_PER_CATEGORY} produits x {len(OPENFOODFACTS_CATEGORIES)} catégories")
    df_off = fetch_openfoodfacts_products(
        queries=OPENFOODFACTS_CATEGORIES,
        products_per_query=OPENFOODFACTS_PRODUCTS_PER_CATEGORY
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
    # ÉTAPE 2 : Transformation (Aurélien)
    # ========================================
    # TODO: Ajouter l'import et l'appel de la fonction de transformation
    # from src.transform import main as transform_data
    # transform_data()

    # ========================================
    # ÉTAPE 3 : Enrichissement/Stockage (Jules)
    # ========================================
    # TODO: Ajouter l'import et l'appel de la fonction d'enrichissement
    # from src.enrichment import main as enrich_data
    # enrich_data()

    # ========================================
    # ÉTAPE 4 : Streamlit IA/Chatbot (Juba)
    # ========================================
    # TODO: Lancer l'application Streamlit
    # import subprocess
    # subprocess.run(["streamlit", "run", "src/app.py"])

    print("\n" + "=" * 60)
    print("PIPELINE TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
