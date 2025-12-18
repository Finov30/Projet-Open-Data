"""
Étape 1 : Récupération des données et stockage en CSV

Ce script récupère les données depuis :
- OpenFoodFacts (API)
- CIQUAL (data.gouv.fr) - optionnel

Et les stocke dans data/raw/ en format CSV pour les étapes suivantes.

Usage:
    python -m src.data.fetch_data
"""

import pandas as pd
from pathlib import Path
from .clients.openfoodfacts import OpenFoodFactsClient
from .clients.ciqual import CiqualClient


# Dossier de sortie pour les données brutes
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def fetch_openfoodfacts_products(queries: list[str], products_per_query: int = 50) -> pd.DataFrame:
    """Récupère des produits depuis OpenFoodFacts."""
    client = OpenFoodFactsClient()
    all_products = []

    for query in queries:
        print(f"  Recherche: '{query}'...")
        try:
            products = client.search_products(query, page_size=products_per_query)
            for p in products:
                row = {
                    "code": p.get("code"),
                    "product_name": p.get("product_name"),
                    "brands": p.get("brands"),
                    "categories": p.get("categories"),
                    "nutriscore_grade": p.get("nutriscore_grade"),
                    "nova_group": p.get("nova_group"),
                    "ecoscore_grade": p.get("ecoscore_grade"),
                    "energy_kcal_100g": p.get("nutriments", {}).get("energy-kcal_100g"),
                    "fat_100g": p.get("nutriments", {}).get("fat_100g"),
                    "saturated_fat_100g": p.get("nutriments", {}).get("saturated-fat_100g"),
                    "carbohydrates_100g": p.get("nutriments", {}).get("carbohydrates_100g"),
                    "sugars_100g": p.get("nutriments", {}).get("sugars_100g"),
                    "fiber_100g": p.get("nutriments", {}).get("fiber_100g"),
                    "proteins_100g": p.get("nutriments", {}).get("proteins_100g"),
                    "salt_100g": p.get("nutriments", {}).get("salt_100g"),
                    "ingredients_text": p.get("ingredients_text_fr") or p.get("ingredients_text"),
                    "allergens": p.get("allergens"),
                    "additives_n": p.get("additives_n"),
                    "image_url": p.get("image_front_url") or p.get("image_url"),
                }
                all_products.append(row)
            print(f"    -> {len(products)} produits")
        except Exception as e:
            print(f"    -> Erreur: {e}")

    df = pd.DataFrame(all_products)
    if not df.empty:
        df = df.drop_duplicates(subset=["code"])
    return df


def fetch_ciqual_data() -> pd.DataFrame:
    """Télécharge les données CIQUAL."""
    client = CiqualClient()
    print("  Téléchargement depuis data.gouv.fr...")
    try:
        df = client.download_data()
        print(f"    -> {len(df)} aliments")
        return df
    except Exception as e:
        print(f"    -> Erreur: {e}")
        return pd.DataFrame()


def main():
    """Point d'entrée principal."""
    print("=" * 50)
    print("ÉTAPE 1 : Récupération des données")
    print("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. OpenFoodFacts
    print("\n[1/2] OpenFoodFacts")
    queries = ["chocolat", "yaourt", "biscuit", "pain", "fromage"]

    df_off = fetch_openfoodfacts_products(queries, products_per_query=20)
    if not df_off.empty:
        off_file = OUTPUT_DIR / "openfoodfacts_products.csv"
        df_off.to_csv(off_file, index=False, encoding="utf-8")
        print(f"  -> Sauvegardé: {off_file} ({len(df_off)} produits)")

    # 2. CIQUAL (optionnel)
    print("\n[2/2] CIQUAL (ANSES)")
    df_ciqual = fetch_ciqual_data()
    if not df_ciqual.empty:
        ciqual_file = OUTPUT_DIR / "ciqual_aliments.csv"
        df_ciqual.to_csv(ciqual_file, index=False, encoding="utf-8")
        print(f"  -> Sauvegardé: {ciqual_file}")

    print("\n" + "=" * 50)
    print("Terminé! Fichiers dans:", OUTPUT_DIR)
    print("=" * 50)


if __name__ == "__main__":
    main()
