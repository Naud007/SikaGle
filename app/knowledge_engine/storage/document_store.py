import json
from pathlib import Path

from app.schemas.document import DocumentMetadata


class DocumentStore:

    def __init__(
        self,
        storage_path="/app/knowledge/processed/documents.json"
    ):

        self.storage_path = Path(
            storage_path
        )

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    # =========================================================
    # CHARGER LES DOCUMENTS
    # =========================================================

    def _load(self):

        if not self.storage_path.exists():

            return []

        try:

            with open(
                self.storage_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(
                    data,
                    list
                ):

                    return data

                return []

        except Exception as e:

            print(
                f"[DOCUMENT STORE] "
                f"Erreur lecture : {e}"
            )

            return []


    # =========================================================
    # SAUVEGARDER LES DOCUMENTS
    # =========================================================

    def _save(
        self,
        documents
    ):

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                documents,
                file,
                ensure_ascii=False,
                indent=2
            )


    # =========================================================
    # AJOUTER DES DOCUMENTS
    # =========================================================

    def add_documents(
        self,
        documents
    ):

        existing_documents = self._load()

        existing_urls = {
            document.get("url")
            for document in existing_documents
            if document.get("url")
        }

        added = 0

        for document in documents:

            if isinstance(
                document,
                DocumentMetadata
            ):

                data = document.model_dump(
                    mode="json"
                )

            elif isinstance(
                document,
                dict
            ):

                data = document

            else:

                continue

            url = data.get(
                "url"
            )

            if (
                url
                and url in existing_urls
            ):

                continue

            existing_documents.append(
                data
            )

            if url:

                existing_urls.add(
                    url
                )

            added += 1

        self._save(
            existing_documents
        )

        print(
            f"[DOCUMENT STORE] "
            f"{added} nouveau(x) document(s) ajouté(s)."
        )

        print(
            f"[DOCUMENT STORE] "
            f"Total : {len(existing_documents)} document(s)."
        )

        print(
            f"[DOCUMENT STORE] "
            f"Fichier : {self.storage_path}"
        )

        return {
            "added": added,
            "total": len(
                existing_documents
            ),
            "file": str(
                self.storage_path
            )
        }


    # =========================================================
    # RÉCUPÉRER TOUS LES DOCUMENTS
    # =========================================================

    def get_all(self):

        print(
            f"[DOCUMENT STORE] "
            f"Recherche du fichier : {self.storage_path}"
        )

        print(
            f"[DOCUMENT STORE] "
            f"Fichier existe : "
            f"{self.storage_path.exists()}"
        )

        if self.storage_path.exists():

            print(
                f"[DOCUMENT STORE] "
                f"Taille du fichier : "
                f"{self.storage_path.stat().st_size} octets"
            )

        documents = self._load()

        print(
            f"[DOCUMENT STORE] "
            f"Documents chargés : {len(documents)}"
        )

        return documents


    # =========================================================
    # RÉCUPÉRER UN LOT DE DOCUMENTS
    # =========================================================

    def get_batch(
        self,
        limit=100,
        offset=0
    ):

        """
        Récupère uniquement une portion des documents.

        Exemple :

        get_batch(
            limit=100,
            offset=0
        )

        -> Documents 0 à 99

        get_batch(
            limit=100,
            offset=100
        )

        -> Documents 100 à 199
        """

        if limit <= 0:

            raise ValueError(
                "Le paramètre limit doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "Le paramètre offset ne peut pas être négatif."
            )

        documents = self._load()

        total_documents = len(
            documents
        )

        batch = documents[
            offset:
            offset + limit
        ]

        print(
            f"[DOCUMENT STORE] "
            f"Batch demandé : "
            f"offset={offset}, "
            f"limit={limit}"
        )

        print(
            f"[DOCUMENT STORE] "
            f"Total documents : "
            f"{total_documents}"
        )

        print(
            f"[DOCUMENT STORE] "
            f"Documents retournés : "
            f"{len(batch)}"
        )

        return batch


    # =========================================================
    # COMPTER LES DOCUMENTS
    # =========================================================

    def count(self):

        return len(
            self._load()
        )


    # =========================================================
    # VIDER LE STOCKAGE
    # =========================================================

    def clear(self):

        self._save([])

        print(
            "[DOCUMENT STORE] "
            "Base documentaire vidée."
        )
