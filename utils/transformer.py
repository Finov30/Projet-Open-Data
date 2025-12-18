from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


# ============================================================
# OpenFoodFacts
# ============================================================
def transform_openfoodfacts() -> pd.DataFrame:
    file_path = RAW_DIR / "openfoodfacts_products.csv"
    df = pd.read_csv(file_path)

    # Normalisation des noms de colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Colonnes numériques
    numeric_cols = [
        "energy_kcal_100g", "fat_100g", "saturated_fat_100g",
        "carbohydrates_100g", "sugars_100g", "fiber_100g",
        "proteins_100g", "salt_100g", "additives_n", "nova_group"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Encodage Nutri-score / Eco-score
    score_mapping = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

    df["nutriscore_numeric"] = (
        df["nutriscore_grade"]
        .str.lower()
        .map(score_mapping)
    )

    df["ecoscore_numeric"] = (
        df["ecoscore_grade"]
        .str.lower()
        .map(score_mapping)
    )

    # Nettoyage texte
    text_cols = [
        "product_name", "brands", "categories",
        "ingredients_text", "allergens"
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").str.strip()

    # Suppression des produits sans nom
    df = df[df["product_name"] != ""]

    return df


# ============================================================
# CIQUAL
# ============================================================
def transform_ciqual() -> pd.DataFrame:
    file_path = RAW_DIR / "ciqual_aliments.csv"
    df = pd.read_csv(file_path)

    # Normalisation colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Colonnes nutritionnelles = tout sauf identifiants
    id_cols = [
        "alim_code", "alim_nom_fr",
        "alim_grp_code", "alim_grp_nom_fr",
        "alim_ssgrp_code", "alim_ssgrp_nom_fr"
    ]

    for col in df.columns:
        if col not in id_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Nettoyage texte
    df["alim_nom_fr"] = df["alim_nom_fr"].fillna("").str.strip()

    return df


# ============================================================
# Orchestrateur
# ============================================================
def run_transformations():
    print("\n" + "=" * 60)
    print("ÉTAPE 2 : Transformation des données")
    print("=" * 60)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # OpenFoodFacts
    print("\n[1/2] Transformation OpenFoodFacts")
    df_off = transform_openfoodfacts()
    off_out = PROCESSED_DIR / "openfoodfacts_products_clean.csv"
    df_off.to_csv(off_out, index=False, encoding="utf-8")
    print(f"  -> Sauvegardé: {off_out} ({len(df_off)} lignes)")

    # CIQUAL
    print("\n[2/2] Transformation CIQUAL")
    df_ciqual = transform_ciqual()
    ciqual_out = PROCESSED_DIR / "ciqual_aliments_clean.csv"
    df_ciqual.to_csv(ciqual_out, index=False, encoding="utf-8")
    print(f"  -> Sauvegardé: {ciqual_out} ({len(df_ciqual)} lignes)")
