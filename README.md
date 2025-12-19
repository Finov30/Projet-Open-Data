# NutriScan — L'assistant nutrition intelligent

## 📋 Description
NutriScan est une application intelligente qui aide les consommateurs à mieux comprendre la composition nutritionnelle des produits alimentaires. 
Grâce à l’IA, elle analyse automatiquement les informations nutritionnelles à partir d’un scan ou d’une recherche, compare les produits et recommande des alternatives plus saines adaptées aux préférences de l’utilisateur. 
Un chatbot nutritionnel complète l’expérience en répondant aux questions sur les ingrédients, additifs et allergènes.

## 🎯 Fonctionnalités
- Import et normalisation des jeux de données bruts (OpenFoodFacts, CIQUAL).
- Pipeline ETL pour extraction, nettoyage, enrichissement et export des données.
- Détection automatique des types de colonnes (numériques, dates, catégorielles).
- Interface Streamlit pour exploration des données, filtres avancés et visualisations rapides.
- Chatbot IA utilisant les modules dans le dossier `src/ia` (gestion de modèles, prompts, analyse produit, recommandations).
- Support pour exécuter des modèles locaux via Ollama (HTTP ou CLI).
- Téléchargement des jeux filtrés au format CSV.
- Tests unitaires pour les composants IA (`tests/test_ia.py`).
- Configuration via fichier `.env` et intégration simple à la CI / packaging Python.

## 🛠️ Installation

```bash
# Cloner le repog
git clone https://github.com/Finov30/Projet-Open-Data
```

# Installer avec uv
```bash
uv sync
```

# Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

## 🚀 Lancement

```bash
uv run streamlit run app.py
```

## 📊 Sources de données
- [Source 1](https://openfoodfacts.github.io/openfoodfacts-server/api/) - OpenFoodFacts API : Base de produits alimentaires
- [Source 2](https://www.data.gouv.fr/fr/datasets/table-de-composition-nutritionnelle-des-aliments-ciqual/) - Tables de composition nutritionnelle (ANSES) : Données de référence

## 👥 Équipe
- Samuel ABID
- Jules CAPEL
- Juba AIT ABDELMALEK
- Aurélien LARIVIERE

## 📄 Licence
MIT