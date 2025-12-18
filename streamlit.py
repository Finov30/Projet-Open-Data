import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from src.ia.chatbot import NutritionChatbot
from src.ia.product_analyzer import ProductAnalyzer
from src.ia.recommender import ProductRecommender

# ============================================================
# Configuration
# ============================================================
st.set_page_config(layout="wide", page_title="Explorateur OpenFoodFacts & CIQUAL")

DATASETS = {
    "OpenFoodFacts (transformé)": Path("data/processed/off_transformed.parquet"),
    "CIQUAL (transformé)": Path("data/processed/ciqual_transformed.parquet"),
}

HIDDEN_COLUMNS = {
    "code",
    "join_key",
    "_dataset",
    "_source_file",
    "_load_error",
}

# ============================================================
# Utils chargement
# ============================================================
@st.cache_data
def load_parquet(path: Path) -> pd.DataFrame:
    try:
        return pd.read_parquet(path)
    except Exception as e:
        return pd.DataFrame({"_load_error": [str(e)]})


def normalize_text(s: pd.Series) -> pd.Series:
    return (
        s.fillna("")
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(r"[^a-z0-9 ]", "", regex=True)
        .str.strip()
    )


@st.cache_data
def load_joined_data():
    off = load_parquet(DATASETS["OpenFoodFacts (transformé)"])
    ciqual = load_parquet(DATASETS["CIQUAL (transformé)"])

    if off.empty or ciqual.empty:
        return pd.DataFrame()

    off = off.copy()
    ciqual = ciqual.copy()

    off["join_key"] = normalize_text(off["product_name"])
    ciqual["join_key"] = normalize_text(ciqual["alim_nom_fr"])

    return off.merge(ciqual, on="join_key", how="inner", suffixes=("_off", "_ciqual"))


# ============================================================
# Sidebar – sélection dataset
# ============================================================
st.sidebar.title("Chargement des données")

mode = st.sidebar.radio(
    "Jeu de données",
    ["OpenFoodFacts", "CIQUAL", "Jointure OFF × CIQUAL"],
)

if mode == "OpenFoodFacts":
    df = load_parquet(DATASETS["OpenFoodFacts (transformé)"])
elif mode == "CIQUAL":
    df = load_parquet(DATASETS["CIQUAL (transformé)"])
else:
    df = load_joined_data()

if df.empty:
    st.error("Impossible de charger les données.")
    st.stop()

st.sidebar.success("Données transformées uniquement")

# Colonnes autorisées UI
UI_COLUMNS = [c for c in df.columns if c not in HIDDEN_COLUMNS]


# ============================================================
# Détection colonnes
# ============================================================
def detect_columns(df):
    date_cols, num_cols, cat_cols = [], [], []
    for c in df.columns:
        if c in HIDDEN_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            num_cols.append(c)
        else:
            try:
                s = pd.to_datetime(df[c], errors="coerce")
                if s.notna().sum() > len(s) * 0.5:
                    date_cols.append(c)
                else:
                    cat_cols.append(c)
            except Exception:
                cat_cols.append(c)
    return date_cols, num_cols, cat_cols


date_cols, num_cols, cat_cols = detect_columns(df)

# ============================================================
# Filtres
# ============================================================
st.sidebar.header("Filtres")

show_cols = st.sidebar.multiselect(
    "Colonnes affichées",
    options=UI_COLUMNS,
    default=UI_COLUMNS
)

text_search = st.sidebar.text_input("Recherche texte")

num_filters = {}
for c in [c for c in num_cols if c in UI_COLUMNS][:6]:
    col = pd.to_numeric(df[c], errors="coerce")
    mn, mx = float(np.nanmin(col)), float(np.nanmax(col))
    if np.isfinite(mn) and np.isfinite(mx) and mn != mx:
        lo, hi = st.sidebar.slider(c, mn, mx, (mn, mx))
        num_filters[c] = (lo, hi)


def apply_filters(df):
    out = df.copy()

    if text_search:
        mask = pd.Series(False, index=out.index)
        for c in out.select_dtypes(include="object").columns:
            if c in HIDDEN_COLUMNS:
                continue
            mask |= out[c].astype(str).str.contains(text_search, case=False, na=False)
        out = out[mask]

    for c, (lo, hi) in num_filters.items():
        out[c] = pd.to_numeric(out[c], errors="coerce")
        out = out[(out[c] >= lo) & (out[c] <= hi)]

    return out


df_f = apply_filters(df)


# ============================================================
# Main UI
# ============================================================
st.title("Explorateur de données")
st.caption(f"Mode : **{mode}**")

left, right = st.columns([2, 1])

with left:
    st.subheader("Aperçu")
    st.write(f"{len(df_f)} lignes")

    st.dataframe(
        df_f[show_cols].reset_index(drop=True),
        use_container_width=True,
        height=400
    )

    if num_cols:
        st.subheader(f"Histogramme – {num_cols[0]}")
        st.bar_chart(df_f[num_cols[0]].dropna().value_counts().head(40))

    csv = df_f[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger CSV", csv, "export.csv", "text/csv")

with right:
    st.subheader("Statistiques")
    st.write(df_f[show_cols].describe(include="all").transpose())


# ============================================================
# IA
# ============================================================
@st.cache_resource
def init_ai():
    return NutritionChatbot(), ProductAnalyzer(), ProductRecommender()


chatbot, analyzer, recommender = init_ai()

# ============================================================
# Produit actif
# ============================================================
st.sidebar.header("Produit actif")

if "product_name" in UI_COLUMNS:
    product_col = "product_name"
elif "alim_nom_fr" in UI_COLUMNS:
    product_col = "alim_nom_fr"
else:
    product_col = UI_COLUMNS[0]

selected_product = st.sidebar.selectbox(
    "Choisir un produit",
    options=df[product_col].dropna().unique()
)

current_product = df[df[product_col] == selected_product].iloc[0].to_dict()

# ============================================================
# Analyse IA
# ============================================================
st.header("Analyse nutritionnelle IA")

if st.button("Analyser ce produit"):
    with st.spinner("Analyse en cours..."):
        result = analyzer.analyze(current_product)

    if result["success"]:
        st.markdown(result["analysis"])
        st.caption(f"Modèle utilisé : {result['model_used']}")
    else:
        st.error(result["error"])


# ============================================================
# Chat
# ============================================================
st.header("Chat nutritionnel")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("chat_form"):
    user_message = st.text_area("Votre question")
    submitted = st.form_submit_button("Envoyer")

    if submitted and user_message.strip():
        response = chatbot.chat(
            user_message=user_message,
            context={"current_product": current_product}
        )

        if response["success"]:
            st.session_state.chat_history.extend([
                ("Vous", user_message),
                ("NutriScan", response["response"]),
            ])
        else:
            st.error(response["error"])

for role, msg in st.session_state.chat_history:
    st.markdown(f"**{role} :** {msg}")


# ============================================================
# Suggestions
# ============================================================
st.subheader("Suggestions de questions")

suggestions = chatbot.suggest_questions(context={"current_product": current_product})

cols = st.columns(2)
for i, q in enumerate(suggestions):
    if cols[i % 2].button(q):
        response = chatbot.chat(q, context={"current_product": current_product})
        if response["success"]:
            st.session_state.chat_history.extend([
                ("Vous", q),
                ("NutriScan", response["response"]),
            ])


# ============================================================
# Recommandations
# ============================================================
st.header("Produits alternatifs plus sains")

if st.button("Suggérer des alternatives"):
    candidates = df.sample(min(10, len(df))).to_dict(orient="records")

    result = recommender.recommend(
        original_product=current_product,
        candidate_products=candidates
    )

    if result["success"]:
        st.markdown(result["recommendations"])
        st.caption(f"Modèle utilisé : {result['model_used']}")
    else:
        st.error(result["error"])
