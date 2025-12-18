"""Client pour les données CIQUAL (ANSES) - Étape 1: Récupération des données."""

import httpx
import pandas as pd
from io import BytesIO


class CiqualClient:
    """Client simple pour télécharger les données CIQUAL depuis ciqual.anses.fr."""

    # URL directe du fichier Excel CIQUAL 2020 (site officiel ANSES)
    CIQUAL_EXCEL_URL = "https://ciqual.anses.fr/cms/sites/default/files/inline-files/Table%20Ciqual%202020_FR_2020%2007%2007.xls"

    def __init__(self, timeout: float = 120.0):
        self.timeout = timeout

    def download_data(self) -> pd.DataFrame:
        """Télécharge les données CIQUAL depuis ciqual.anses.fr (data.gouv.fr).

        Returns:
            DataFrame avec les données brutes CIQUAL (3185 aliments)
        """
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(self.CIQUAL_EXCEL_URL)
            response.raise_for_status()

        # Lire le fichier Excel directement en mémoire
        df = pd.read_excel(BytesIO(response.content))
        return df
