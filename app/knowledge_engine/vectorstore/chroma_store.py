from pathlib import Path

import chromadb

from app.core import settings


class ChromaStore:
    """
    Gestionnaire de la base vectorielle ChromaDB.
    """

    def __init__(self):

        db_path = Path(settings.CHROMA_PATH)

        db_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(db_path)
        )

        self.collection = self.client.get_or_create_collection(
            name="knowledge"
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

            return (
                len(result["ids"]) > 0
            )

        except Exception:

            return False

    def add_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ):

        ids = [
            f"{doc_id}_{i}"
            for i in range(
                len(chunks)
            )
        ]

        metadatas = [
            metadata.copy()
            for _ in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
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
    ):

        return self.collection.count()
