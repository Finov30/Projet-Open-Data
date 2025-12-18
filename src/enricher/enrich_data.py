from pathlib import Path
import pandas as pd

# ===============================
# CONFIG PATHS (data/ à la racine)
# ===============================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
ENRICHED_DIR = DATA_DIR / "enriched"

OFF_CSV = PROCESSED_DIR / "off_transformed.csv"
CIQUAL_CSV = PROCESSED_DIR / "ciqual_transformed.csv"

OFF_PARQUET = PROCESSED_DIR / "off_transformed.parquet"
CIQUAL_PARQUET = PROCESSED_DIR / "ciqual_transformed.parquet"

OUTPUT_FILE = ENRICHED_DIR / "off_enriched.parquet"


# ===============================
# ENRICHMENT LOGIC
# ===============================
def compute_energy_density(row):
    """kcal pour 100g"""
    return row.get("energy_kcal_100g")


def compute_protein_ratio(row):
    """protéines / énergie"""
    energy = row.get("energy_kcal_100g", 0)
    if energy and energy > 0:
        return row.get("proteins_100g", 0) / energy
    return None


def enrich_off_with_ciqual(df_off: pd.DataFrame, df_ciqual: pd.DataFrame) -> pd.DataFrame:
    """Enrichit OpenFoodFacts avec CIQUAL via une jointure sur le nom normalisé."""

    df_off["product_name_norm"] = (
        df_off["product_name"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-zàâçéèêëîïôûùüÿñæœ ]", "", regex=True)
    )

    df_ciqual["food_name_norm"] = (
        df_ciqual["alim_nom_fr"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-zàâçéèêëîïôûùüÿñæœ ]", "", regex=True)
    )

    df = df_off.merge(
        df_ciqual,
        left_on="product_name_norm",
        right_on="food_name_norm",
        how="left",
        suffixes=("_off", "_ciqual"),
    )

    df["energy_density"] = df.apply(compute_energy_density, axis=1)
    df["protein_ratio"] = df.apply(compute_protein_ratio, axis=1)

    return df


# ===============================
# MAIN
# ===============================
def main():
    print("\n" + "=" * 60)
    print("ÉTAPE 3 : CSV → Parquet + Enrichissement")
    print("=" * 60)

    if not OFF_CSV.exists() or not CIQUAL_CSV.exists():
        raise FileNotFoundError("Fichiers CSV transformés manquants")

    # --- CSV → DataFrame
    df_off = pd.read_csv(OFF_CSV)
    df_ciqual = pd.read_csv(CIQUAL_CSV)

    # --- Sauvegarde Parquet (PROCESSED)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_off.to_parquet(OFF_PARQUET, engine="pyarrow", index=False)
    df_ciqual.to_parquet(CIQUAL_PARQUET, engine="pyarrow", index=False)

    print("→ Conversion CSV → Parquet terminée (processed/)")

    # --- Enrichissement
    df_enriched = enrich_off_with_ciqual(df_off, df_ciqual)

    # --- Sauvegarde Parquet enrichi
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

    df_enriched.to_parquet(
        OUTPUT_FILE,
        engine="pyarrow",
        index=False
    )

    print(f"→ Dataset enrichi sauvegardé : {OUTPUT_FILE}")
    print(f"→ Lignes : {len(df_enriched)}")


if __name__ == "__main__":
    main()
