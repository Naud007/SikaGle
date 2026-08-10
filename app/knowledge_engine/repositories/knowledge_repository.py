from app.knowledge_engine.vectorstore import (
    SupabaseStore,
)


class KnowledgeRepository:
    """
    Dépôt d'accès aux connaissances indexées.

    La persistance vectorielle est assurée par
    Supabase + pgvector.

    Le reste de l'application ne dépend donc
    pas directement de Supabase.
    """

    def __init__(self):

        self.vectorstore = SupabaseStore()

    # =========================================================
    # RECHERCHE VECTORIELLE
    # =========================================================

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ):

        return self.vectorstore.search(
            embedding=embedding,
            n_results=top_k,
        )

    # =========================================================
    # AJOUTER UN DOCUMENT
    # =========================================================

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

    # =========================================================
    # EXISTENCE
    # =========================================================

    def exists(
        self,
        doc_id: str,
    ) -> bool:

        return self.vectorstore.exists(
            doc_id
        )

    # =========================================================
    # SUPPRESSION
    # =========================================================

    def delete_document(
        self,
        doc_id: str,
    ) -> None:

        self.vectorstore.delete_document(
            doc_id
        )

    # =========================================================
    # RÉCUPÉRATION
    # =========================================================

    def get_document(
        self,
        doc_id: str,
    ):

        return self.vectorstore.get_document(
            doc_id
        )

    # =========================================================
    # COMPTE
    # =========================================================

    def count(
        self,
    ) -> int:

        return self.vectorstore.count()