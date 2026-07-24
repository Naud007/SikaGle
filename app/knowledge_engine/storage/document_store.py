from pathlib import Path
import json
from typing import List, Optional

from app.schemas.document import DocumentMetadata


class DocumentStore:
    """
    Stockage persistant des documents du Knowledge Engine.

    Pour le moment, les documents sont stockés dans un fichier JSON.
    Cette première version permet de :
    - sauvegarder les documents
    - éviter les doublons
    - charger les documents existants
    - rechercher des documents
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None
    ):
        # -------------------------------------------------
        # Chemin par défaut
        # -------------------------------------------------

        if storage_path is None:

            storage_path = (
                Path("/app/knowledge")
                / "processed"
                / "documents.json"
            )

        self.storage_path = Path(
            storage_path
        )

        # Créer le dossier si nécessaire
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"[DOCUMENT STORE] "
            f"Stockage : {self.storage_path}"
        )

    # =====================================================
    # CONVERSION DOCUMENT -> DICTIONNAIRE
    # =====================================================

    def _document_to_dict(
        self,
        document: DocumentMetadata
    ):

        # Pydantic V2
        if hasattr(
            document,
            "model_dump"
        ):

            data = document.model_dump(
                mode="json"
            )

        # Compatibilité Pydantic V1
        else:

            data = document.dict()

        return data

    # =====================================================
    # CONVERSION DICTIONNAIRE -> DOCUMENT
    # =====================================================

    def _dict_to_document(
        self,
        data: dict
    ):

        return DocumentMetadata(
            **data
        )

    # =====================================================
    # CHARGER LES DOCUMENTS
    # =====================================================

    def load_all(
        self
    ) -> List[DocumentMetadata]:

        if not self.storage_path.exists():

            print(
                "[DOCUMENT STORE] "
                "Aucun document stocké."
            )

            return []

        try:

            with open(
                self.storage_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            documents = []

            for item in data:

                try:

                    document = (
                        self._dict_to_document(
                            item
                        )
                    )

                    documents.append(
                        document
                    )

                except Exception as e:

                    print(
                        "[DOCUMENT STORE] "
                        f"Document invalide ignoré : "
                        f"{e}"
                    )

            print(
                "[DOCUMENT STORE] "
                f"{len(documents)} document(s) "
                "chargé(s)."
            )

            return documents

        except Exception as e:

            print(
                "[DOCUMENT STORE] "
                f"Erreur lecture : {e}"
            )

            return []

    # =====================================================
    # SAUVEGARDER TOUS LES DOCUMENTS
    # =====================================================

    def save_all(
        self,
        documents: List[DocumentMetadata]
    ):

        data = []

        for document in documents:

            try:

                data.append(
                    self._document_to_dict(
                        document
                    )
                )

            except Exception as e:

                print(
                    "[DOCUMENT STORE] "
                    f"Document ignoré : {e}"
                )

        # Écriture atomique :
        # on écrit d'abord dans un fichier temporaire

        temp_path = (
            self.storage_path.with_suffix(
                ".tmp"
            )
        )

        try:

            with open(
                temp_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            # Remplacer l'ancien fichier
            temp_path.replace(
                self.storage_path
            )

            print(
                "[DOCUMENT STORE] "
                f"{len(data)} document(s) "
                f"enregistré(s)."
            )

            print(
                "[DOCUMENT STORE] "
                f"Fichier : "
                f"{self.storage_path}"
            )

        except Exception as e:

            print(
                "[DOCUMENT STORE] "
                f"Erreur sauvegarde : {e}"
            )

            # Nettoyer le fichier temporaire
            if temp_path.exists():

                temp_path.unlink()

            raise

    # =====================================================
    # AJOUTER DES DOCUMENTS
    # =====================================================

    def add_documents(
        self,
        documents: List[DocumentMetadata]
    ):

        if not documents:

            print(
                "[DOCUMENT STORE] "
                "Aucun document à ajouter."
            )

            return 0

        # Charger les documents existants

        existing_documents = (
            self.load_all()
        )

        # Index des URLs existantes

        existing_urls = set()

        for document in existing_documents:

            try:

                url = str(
                    document.url
                )

                if url:

                    existing_urls.add(
                        url
                    )

            except Exception:

                continue

        new_documents = []

        duplicate_count = 0

        # Ajouter uniquement les nouveaux

        for document in documents:

            try:

                url = str(
                    document.url
                )

            except Exception:

                url = ""

            # Si l'URL existe déjà
            if (
                url
                and url in existing_urls
            ):

                duplicate_count += 1

                continue

            # Ajouter le document

            new_documents.append(
                document
            )

            if url:

                existing_urls.add(
                    url
                )

        # Fusionner

        all_documents = (
            existing_documents
            + new_documents
        )

        # Sauvegarder

        self.save_all(
            all_documents
        )

        print(
            "[DOCUMENT STORE] "
            f"{len(new_documents)} "
            "nouveau(x) document(s) ajouté(s)."
        )

        print(
            "[DOCUMENT STORE] "
            f"{duplicate_count} doublon(s) ignoré(s)."
        )

        print(
            "[DOCUMENT STORE] "
            f"Total : "
            f"{len(all_documents)} document(s)."
        )

        return len(
            new_documents
        )

    # =====================================================
    # COMPTER LES DOCUMENTS
    # =====================================================

    def count(
        self
    ) -> int:

        documents = (
            self.load_all()
        )

        return len(
            documents
        )

    # =====================================================
    # RECHERCHE SIMPLE
    # =====================================================

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[DocumentMetadata]:

        if not query:

            return []

        query = (
            query
            .strip()
            .lower()
        )

        if not query:

            return []

        documents = (
            self.load_all()
        )

        results = []

        for document in documents:

            # ---------------------------------------------
            # Titre
            # ---------------------------------------------

            title = str(
                getattr(
                    document,
                    "title",
                    ""
                )
            ).lower()

            # ---------------------------------------------
            # Description
            # ---------------------------------------------

            description = str(
                getattr(
                    document,
                    "description",
                    ""
                )
            ).lower()

            # ---------------------------------------------
            # Source
            # ---------------------------------------------

            source = str(
                getattr(
                    document,
                    "source",
                    ""
                )
            ).lower()

            # ---------------------------------------------
            # Recherche
            # ---------------------------------------------

            text = (
                f"{title} "
                f"{description} "
                f"{source}"
            )

            if query in text:

                results.append(
                    document
                )

            # Limite des résultats

            if len(results) >= limit:

                break

        print(
            "[DOCUMENT STORE] "
            f"Recherche : '{query}'"
        )

        print(
            "[DOCUMENT STORE] "
            f"{len(results)} résultat(s)."
        )

        return results
