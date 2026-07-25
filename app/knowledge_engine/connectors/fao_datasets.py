import requests
from pathlib import Path

from app.knowledge_engine.config import config


class FAODatasetsDownloader:

    def __init__(self):

        # =====================================================
        # DOSSIER DE STOCKAGE DES DATASETS FAO
        # =====================================================

        self.storage_dir = (
            config.raw_dir
            / "fao"
            / "datasets"
        )

        # Créer automatiquement le dossier
        # s'il n'existe pas

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "[FAO DATASET] "
            f"Dossier de stockage : "
            f"{self.storage_dir}"
        )


    # =========================================================
    # TÉLÉCHARGER UN DATASET FAO
    # ET LE SAUVEGARDER SUR DISQUE
    # =========================================================

    def download(
        self,
        url: str,
        filename: str
    ):

        print(
            "[FAO DATASET] "
            f"Téléchargement : "
            f"{filename}"
        )

        print(
            "[FAO DATASET] "
            f"URL : "
            f"{url}"
        )


        # =====================================================
        # CHEMIN LOCAL DU FICHIER
        # =====================================================

        file_path = (
            self.storage_dir
            / filename
        )


        # =====================================================
        # ÉVITER DE RETÉLÉCHARGER UN FICHIER EXISTANT
        # =====================================================

        if file_path.exists():

            file_size = (
                file_path.stat().st_size
            )

            print(
                "[FAO DATASET] "
                f"Dataset déjà présent : "
                f"{file_path}"
            )

            print(
                "[FAO DATASET] "
                f"Taille : "
                f"{file_size} octets"
            )

            return file_path


        # =====================================================
        # TÉLÉCHARGEMENT HTTP
        # =====================================================

        try:

            response = requests.get(
                url,
                timeout=120
            )

            response.raise_for_status()


            # =================================================
            # SAUVEGARDE SUR DISQUE
            # =================================================

            file_path.write_bytes(
                response.content
            )


            # =================================================
            # VÉRIFICATION
            # =================================================

            if not file_path.exists():

                raise RuntimeError(
                    "Le fichier dataset "
                    "n'a pas été créé."
                )


            file_size = (
                file_path.stat().st_size
            )


            print(
                "[FAO DATASET] "
                f"Dataset enregistré : "
                f"{file_path}"
            )

            print(
                "[FAO DATASET] "
                f"Taille : "
                f"{file_size} octets"
            )


            # =================================================
            # RETOURNER LE CHEMIN LOCAL
            # =================================================

            return file_path


        except requests.RequestException as e:

            print(
                "[FAO DATASET] "
                "Erreur HTTP :",
                e
            )

            raise


        except Exception as e:

            print(
                "[FAO DATASET] "
                "Erreur sauvegarde :",
                e
            )

            raise
