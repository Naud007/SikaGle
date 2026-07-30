from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class KnowledgeRepository:
    """
    Dépôt d'accès aux connaissances indexées.

    Cette classe encapsule les interactions avec le stockage
    vectoriel afin d'isoler le reste de l'application des
    détails d'implémentation de ChromaDB.
    """

    def __init__(self):

        self.vectorstore = ChromaStore()

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ):

        return self.vectorstore.search(
            embedding=embedding,
            n_results=top_k,
        )

    def add_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> None:

        self.vectorstore.add_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )

    def exists(
        self,
        doc_id: str,
    ) -> bool:

        return self.vectorstore.exists(
            doc_id
        )

    def delete_document(
        self,
        doc_id: str,
    ) -> None:

        self.vectorstore.delete_document(
            doc_id
        )

    def get_document(
        self,
        doc_id: str,
    ):

        return self.vectorstore.get_document(
            doc_id
        )

    def count(
        self,
    ) -> int:

        return self.vectorstore.count()
