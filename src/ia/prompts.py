"""
Prompts IA centralisés pour NutriScan.
"""

class NutritionPrompts:
    """Collection de prompts pour les fonctionnalités IA NutriScan."""

    @staticmethod
    def product_analysis_system_prompt() -> str:
        return (
            "Tu es un nutritionniste professionnel et pédagogue. "
            "Tu expliques les informations nutritionnelles de façon claire, "
            "factuelle et accessible au grand public, sans alarmisme."
        )

    @staticmethod
    def product_analysis_user_prompt(product: dict) -> str:
        return f"""
Analyse le produit alimentaire suivant :

Nom : {product.get("product_name", "Inconnu")}
Marque : {product.get("brands", "Inconnue")}
Nutri-Score : {product.get("nutriscore_grade", "?" )}
NOVA : {product.get("nova_group", "?" )}

Nutriments (pour 100g) :
{product.get("nutriments", {})}

Additifs :
{product.get("additives_tags", [])}

Explique :
1. La qualité nutritionnelle globale
2. Les points positifs
3. Les points négatifs
4. Pour quel type de consommation ce produit est adapté

Réponds en français, de façon synthétique et structurée.
"""

    @staticmethod
    def recommendation_system_prompt() -> str:
        return (
            "Tu es un expert en nutrition et en comparaison de produits alimentaires. "
            "Tu recommandes des alternatives plus saines tout en restant réaliste "
            "sur le goût, le prix et les habitudes de consommation."
        )

    @staticmethod
    def recommendation_user_prompt(
        original_product: dict,
        candidate_products: list,
        preferences: dict
    ) -> str:
        return f"""
Produit initial :
{original_product.get("product_name")}

Préférences utilisateur :
{preferences}

Produits alternatifs possibles :
{[p.get("product_name") for p in candidate_products]}

Sélectionne 3 alternatives maximum, plus saines que le produit initial.
Explique brièvement chaque recommandation.
"""

    @staticmethod
    def chatbot_system_prompt() -> str:
        return (
            "Tu es NutriScan, un assistant nutrition intelligent. "
            "Tu réponds de façon fiable, pédagogique et bienveillante. "
            "Tu n'établis pas de diagnostic médical."
        )
