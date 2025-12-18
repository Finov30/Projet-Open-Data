"""Client pour l'API OpenFoodFacts - Étape 1: Récupération des données."""

import httpx
from typing import Optional


class OpenFoodFactsClient:
    """Client simple pour récupérer des produits depuis OpenFoodFacts."""

    BASE_URL = "https://world.openfoodfacts.org"

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout
        self.headers = {"User-Agent": "NutriScan/1.0 (contact@nutriscan.app)"}

    def get_product(self, barcode: str) -> Optional[dict]:
        """Récupère les données brutes d'un produit par son code-barres.

        Args:
            barcode: Code-barres du produit

        Returns:
            dict avec les données brutes du produit, ou None si non trouvé
        """
        url = f"{self.BASE_URL}/api/v2/product/{barcode}.json"

        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.get(url)

            if response.status_code != 200:
                return None

            data = response.json()

            if data.get("status") == 0:
                return None

            return data.get("product")

    def search_products(self, query: str, page_size: int = 20) -> list[dict]:
        """Recherche des produits.

        Args:
            query: Terme de recherche
            page_size: Nombre de résultats

        Returns:
            Liste de dicts avec les données brutes des produits
        """
        url = f"{self.BASE_URL}/cgi/search.pl"
        params = {
            "search_terms": query,
            "page_size": min(page_size, 100),
            "json": 1,
            "action": "process",
        }

        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.get(url, params=params)

            if response.status_code != 200:
                return []

            data = response.json()
            return data.get("products", [])
