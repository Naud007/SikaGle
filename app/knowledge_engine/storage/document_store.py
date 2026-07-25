import json
import os
from pathlib import Path

from supabase import create_client, Client

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
    # CHARGER LES DOCUMENTS LOCAUX
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

                data = json.load(
                    file
                )

                if isinstance(
                    data,
                    list
                ):

                    return data

                return []

        except Exception as e:

            print(
                f"[DOCUMENT STORE] "
                f"Erreur lecture fichier local : {e}"
            )

            return []


    # =========================================================
    # SAUVEGARDER LES DOCUMENTS LOCAUX
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
    # AJOUTER DES DOCUMENTS LOCALEMENT
    # =========================================================

    def add_documents(
        self,
        documents
    ):

        existing_documents = (
            self._load()
        )

        existing_urls = {

            document.get(
                "url"
            )

            for document
            in existing_documents

            if document.get(
                "url"
            )

        }

        added = 0

        for document in documents:

            if isinstance(
                document,
                DocumentMetadata
            ):

                data = (
                    document.model_dump(
                        mode="json"
                    )
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
            f"Total : "
            f"{len(existing_documents)} document(s)."
        )

        print(
            f"[DOCUMENT STORE] "
            f"Fichier : "
            f"{self.storage_path}"
        )

        return {

            "added":
                added,

            "total":
                len(
                    existing_documents
                ),

            "file":
                str(
                    self.storage_path
                )

        }


    # =========================================================
    # RÉCUPÉRER TOUS LES DOCUMENTS
    # DEPUIS SUPABASE
    # =========================================================

    def get_all(self):

        print(
            "[DOCUMENT STORE] "
            "Lecture des documents depuis Supabase..."
        )

        try:

            supabase_url = os.getenv(
                "SUPABASE_URL"
            )

            supabase_key = os.getenv(
                "SUPABASE_KEY"
            )

            if not supabase_url:

                raise ValueError(
                    "SUPABASE_URL manquante."
                )

            if not supabase_key:

                raise ValueError(
                    "SUPABASE_KEY manquante."
                )

            supabase: Client = (
                create_client(
                    supabase_url,
                    supabase_key
                )
            )

            # -------------------------------------------------
            # RÉCUPÉRATION PAR LOTS
            # -------------------------------------------------

            documents = []

            batch_size = 1000

            offset = 0

            while True:

                print(
                    "[DOCUMENT STORE] "
                    f"Récupération Supabase : "
                    f"{offset} → "
                    f"{offset + batch_size - 1}"
                )

                response = (

                    supabase

                    .table(
                        "documents_rag"
                    )

                    .select(
                        "id, "
                        "titre, "
                        "organisme, "
                        "version, "
                        "annee, "
                        "langue, "
                        "type_document, "
                        "culture, "
                        "zone_geographique, "
                        "mots_cles, "
                        "source_path, "
                        "content, "
                        "embedding, "
                        "created_at"
                    )

                    .range(
                        offset,
                        offset + batch_size - 1
                    )

                    .execute()

                )

                batch = (
                    response.data
                    or []
                )

                if not batch:

                    break

                documents.extend(
                    batch
                )

                if len(
                    batch
                ) < batch_size:

                    break

                offset += (
                    batch_size
                )

            print(
                "[DOCUMENT STORE] "
                f"{len(documents)} document(s) "
                "chargé(s) depuis Supabase."
            )

            return documents

        except Exception as e:

            print(
                "[DOCUMENT STORE] "
                "Erreur lecture Supabase :",
                e
            )

            return []


    # =========================================================
    # RÉCUPÉRER UN LOT DE DOCUMENTS
    # =========================================================

    def get_batch(
        self,
        limit=100,
        offset=0
    ):

        if limit <= 0:

            raise ValueError(
                "Le paramètre limit "
                "doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "Le paramètre offset "
                "ne peut pas être négatif."
            )

        print(
            "[DOCUMENT STORE] "
            "Lecture d'un batch depuis Supabase : "
            f"offset={offset}, "
            f"limit={limit}"
        )

        try:

            supabase_url = os.getenv(
                "SUPABASE_URL"
            )

            supabase_key = os.getenv(
                "SUPABASE_KEY"
            )

            if not supabase_url:

                raise ValueError(
                    "SUPABASE_URL manquante."
                )

            if not supabase_key:

                raise ValueError(
                    "SUPABASE_KEY manquante."
                )

            supabase: Client = (
                create_client(
                    supabase_url,
                    supabase_key
                )
            )

            response = (

                supabase

                .table(
                    "documents_rag"
                )

                .select(
                    "id, "
                    "titre, "
                    "organisme, "
                    "version, "
                    "annee, "
                    "langue, "
                    "type_document, "
                    "culture, "
                    "zone_geographique, "
                    "mots_cles, "
                    "source_path, "
                    "content, "
                    "embedding, "
                    "created_at"
                )

                .range(
                    offset,
                    offset + limit - 1
                )

                .execute()

            )

            batch = (
                response.data
                or []
            )

            print(
                "[DOCUMENT STORE] "
                f"{len(batch)} document(s) "
                "récupéré(s) depuis Supabase."
            )

            return batch

        except Exception as e:

            print(
                "[DOCUMENT STORE] "
                "Erreur récupération batch Supabase :",
                e
            )

            return []


    # =========================================================
    # COMPTER LES DOCUMENTS
    # =========================================================

    def count(self):

        print(
            "[DOCUMENT STORE] "
            "Comptage des documents Supabase..."
        )

        try:

            supabase_url = os.getenv(
                "SUPABASE_URL"
            )

            supabase_key = os.getenv(
                "SUPABASE_KEY"
            )

            if not supabase_url:

                raise ValueError(
                    "SUPABASE_URL manquante."
                )

            if not supabase_key:

                raise ValueError(
                    "SUPABASE_KEY manquante."
                )

            supabase: Client = (
                create_client(
                    supabase_url,
                    supabase_key
                )
            )

            response = (

                supabase

                .table(
                    "documents_rag"
                )

                .select(
                    "id",
                    count="exact"
                )

                .limit(
                    1
                )

                .execute()

            )

            total = (
                response.count
                or 0
            )

            print(
                "[DOCUMENT STORE] "
                f"Total Supabase : "
                f"{total} document(s)."
            )

            return total

        except Exception as e:

            print(
                "[DOCUMENT STORE] "
                "Erreur comptage Supabase :",
                e
            )

            return 0


    # =========================================================
    # VIDER LE STOCKAGE LOCAL
    # =========================================================

    def clear(self):

        self._save(
            []
        )

        print(
            "[DOCUMENT STORE] "
            "Base documentaire locale vidée."
        )
