from pathlib import Path

import chromadb

from app.core import settings


class ChromaStore:
    """
    Gestionnaire de la base vectorielle ChromaDB.
    """

    COLLECTION_NAME = "knowledge_local"

    def __init__(self):

        db_path = Path(settings.CHROMA_PATH)

        db_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(db_path)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=self.COLLECTION_NAME
            )
        )

    def exists(
        self,
        doc_id: str,
    ) -> bool:
        """
        Vérifie si un document est déjà indexé.
        """

        try:

            result = self.collection.get(
                ids=[f"{doc_id}_0"]
            )

            return len(result["ids"]) > 0

        except Exception:

            return False

    def add_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> None:
        """
        Indexe un document dans ChromaDB.
        """

        ids = []

        documents = []

        metadatas = []

        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):

            ids.append(
                f"{doc_id}_{index}"
            )

            documents.append(chunk)

            # ==========================================
            # NORMALISATION DES MÉTADONNÉES CHROMA
            # ==========================================

            chunk_metadata = {}

            for key, value in metadata.items():

                if value is None:
                    continue

                if isinstance(
                    value,
                    (str, int, float, bool),
                ):

                    chunk_metadata[key] = value

                else:

                    chunk_metadata[key] = str(
                        value
                    )

            # ==========================================
            # MÉTADONNÉES TECHNIQUES
            # ==========================================

            chunk_metadata["document"] = doc_id

            chunk_metadata["chunk_index"] = index

            chunk_metadata["chunk_count"] = total_chunks

            metadatas.append(
                chunk_metadata
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        embedding: list[float],
        n_results: int = 5,
    ):

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
        )

    def count(
        self,
    ) -> int:

        return self.collection.count()

    def delete_document(
        self,
        doc_id: str,
    ) -> None:
        """
        Supprime tous les chunks d'un document.
        """

        self.collection.delete(
            where={
                "document": doc_id,
            }
        )

    def get_document(
        self,
        doc_id: str,
    ):
        """
        Retourne tous les chunks d'un document.
        """

        return self.collection.get(
            where={
                "document": doc_id,
            }
        )