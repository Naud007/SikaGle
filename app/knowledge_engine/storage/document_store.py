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

   def get_all(self):

        print(
            f"[DOCUMENT STORE] "
            f"Recherche du fichier : {self.storage_path}"
        )

        print(
            f"[DOCUMENT STORE] "
            f"Fichier existe : {self.storage_path.exists()}"
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

    def clear(self):

        self._save([])

        print(
            "[DOCUMENT STORE] "
            "Base documentaire vidée."
        )
