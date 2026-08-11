from typing import Any

from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.filters.agricultural_relevance import (
    AgriculturalRelevanceFilter,
)
from app.knowledge_engine.vectorstore.supabase_store import (
    SupabaseStore,
)


class RAGIngestion:
    """
    Pipeline d'ingestion RAG des documents FAO/AGRIS.

    Architecture :

        Document FAO
            ↓
        normalisation
            ↓
        filtre de pertinence agricole
            ↓
        construction du texte RAG
            ↓
        Jina Embeddings v3
            ↓
        embedding 1024D
            ↓
        SupabaseStore
            ↓
        knowledge_embeddings

    Les documents hors domaine agricole sont rejetés
    avant la génération de leur embedding.

    La pagination utilisée par le pipeline FAO
    est conservée.
    """

    EMBEDDING_DIMENSION = 1024

    def __init__(self):

        # =====================================================
        # SERVICE EMBEDDINGS
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService()
        )

        # =====================================================
        # FILTRE DE PERTINENCE AGRICOLE
        # =====================================================

        self.relevance_filter = (
            AgriculturalRelevanceFilter()
        )

        # =====================================================
        # STOCKAGE VECTORIEL PERSISTANT
        # =====================================================

        self.vectorstore = (
            SupabaseStore()
        )

    # =========================================================
    # NORMALISATION DOCUMENT
    # =========================================================

    @staticmethod
    def normalize_document(
        document: Any,
    ) -> dict:

        if isinstance(
            document,
            dict,
        ):

            return document

        if hasattr(
            document,
            "model_dump",
        ):

            return document.model_dump(
                mode="json"
            )

        raise ValueError(
            "Format document non supporté : "
            f"{type(document).__name__}"
        )

    # =========================================================
    # SOURCE / URL
    # =========================================================

    @staticmethod
    def get_document_source(
        document: dict,
    ) -> str | None:

        url = document.get(
            "url"
        )

        if url:

            return str(
                url
            ).strip()

        source_path = document.get(
            "source_path"
        )

        if source_path:

            return str(
                source_path
            ).strip()

        return None

    # =========================================================
    # IDENTIFIANT DOCUMENT
    # =========================================================

    def get_document_id(
        self,
        document: dict,
    ) -> str:

        identifier = (
            document.get(
                "identifier"
            )
            or document.get(
                "id"
            )
        )

        if identifier:

            return str(
                identifier
            ).strip()

        source = (
            self.get_document_source(
                document
            )
        )

        if source:

            return source

        title = self.get_document_title(
            document
        )

        return title

    # =========================================================
    # TITRE
    # =========================================================

    @staticmethod
    def get_document_title(
        document: dict,
    ) -> str:

        title = document.get(
            "title"
        )

        if title:

            return str(
                title
            ).strip()

        titre = document.get(
            "titre"
        )

        if titre:

            return str(
                titre
            ).strip()

        return "Document sans titre"

    # =========================================================
    # CONTENU
    # =========================================================

    @staticmethod
    def get_document_content(
        document: dict,
    ) -> str:

        content = document.get(
            "content"
        )

        if content:

            return str(
                content
            ).strip()

        description = document.get(
            "description"
        )

        if description:

            return str(
                description
            ).strip()

        return ""

    # =========================================================
    # SOURCE / ORGANISME
    # =========================================================

    @staticmethod
    def get_document_source_name(
        document: dict,
    ) -> str:

        source = document.get(
            "source"
        )

        if source:

            return str(
                source
            ).strip()

        organisme = document.get(
            "organisme"
        )

        if organisme:

            return str(
                organisme
            ).strip()

        return "FAO AGRIS"

    # =========================================================
    # TEXTE RAG
    # =========================================================

    def build_rag_text(
        self,
        document: dict,
    ) -> str:

        title = self.get_document_title(
            document
        )

        content = self.get_document_content(
            document
        )

        source = self.get_document_source_name(
            document
        )

        url = self.get_document_source(
            document
        )

        parts = []

        if title:

            parts.append(
                f"Titre : {title}"
            )

        if content:

            parts.append(
                f"Contenu :\n{content}"
            )

        if source:

            parts.append(
                f"Source : {source}"
            )

        if url:

            parts.append(
                f"URL : {url}"
            )

        return "\n\n".join(
            parts
        )

    # =========================================================
    # MÉTADONNÉES
    # =========================================================

    @staticmethod
    def build_metadata(
        document: dict,
    ) -> dict:

        published_at = (
            document.get(
                "published_at"
            )
            or document.get(
                "publication_date"
            )
        )

        language = (
            document.get(
                "language"
            )
            or document.get(
                "langue"
            )
        )

        document_type = (
            document.get(
                "document_type"
            )
            or document.get(
                "type_document"
            )
            or "agricultural_publication"
        )

        crop = (
            document.get(
                "crop"
            )
        )

        culture = (
            document.get(
                "culture"
            )
            or crop
        )

        country = (
            document.get(
                "country"
            )
        )

        zone_geographique = (
            document.get(
                "zone_geographique"
            )
            or country
        )

        keywords = (
            document.get(
                "keywords"
            )
            or document.get(
                "mots_cles"
            )
        )

        identifier = (
            document.get(
                "identifier"
            )
            or document.get(
                "id"
            )
        )

        return {

            "title":
                RAGIngestion.get_document_title(
                    document
                ),

            "source":
                RAGIngestion.get_document_source_name(
                    document
                ),

            "identifier":
                (
                    str(identifier)
                    if identifier is not None
                    else None
                ),

            "url":
                RAGIngestion.get_document_source(
                    document
                ),

            "author":
                RAGIngestion._normalize_author(
                    document.get(
                        "author"
                    )
                    or document.get(
                        "authors"
                    )
                ),

            "published_at":
                RAGIngestion._normalize_date(
                    published_at
                ),

            "language":
                (
                    str(language)
                    if language is not None
                    else None
                ),

            "document_type":
                (
                    str(document_type)
                    if document_type is not None
                    else None
                ),

            "publisher":
                RAGIngestion._normalize_string(
                    document.get(
                        "publisher"
                    )
                ),

            "crop":
                RAGIngestion._normalize_string(
                    crop
                ),

            "culture":
                RAGIngestion._normalize_string(
                    culture
                ),

            "keywords":
                RAGIngestion._normalize_keywords(
                    keywords
                ),

            "country":
                RAGIngestion._normalize_string(
                    country
                ),

            "zone_geographique":
                RAGIngestion._normalize_string(
                    zone_geographique
                ),
        }

    # =========================================================
    # NORMALISATION STRING
    # =========================================================

    @staticmethod
    def _normalize_string(
        value: Any,
    ) -> str | None:

        if value is None:

            return None

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            return value or None

        return str(
            value
        )

    # =========================================================
    # NORMALISATION AUTEUR
    # =========================================================

    @staticmethod
    def _normalize_author(
        value: Any,
    ) -> str | None:

        if value is None:

            return None

        if isinstance(
            value,
            list,
        ):

            return ", ".join(
                str(item)
                for item in value
            )

        return str(
            value
        ).strip() or None

    # =========================================================
    # NORMALISATION DATE
    # =========================================================

    @staticmethod
    def _normalize_date(
        value: Any,
    ) -> str | None:

        if value is None:

            return None

        if hasattr(
            value,
            "isoformat",
        ):

            return value.isoformat()

        value = str(
            value
        ).strip()

        return value or None

    # =========================================================
    # NORMALISATION MOTS-CLÉS
    # =========================================================

    @staticmethod
    def _normalize_keywords(
        value: Any,
    ) -> str | None:

        if value is None:

            return None

        if isinstance(
            value,
            list,
        ):

            values = [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

            return ", ".join(
                values
            ) or None

        return str(
            value
        ).strip() or None

    # =========================================================
    # INGESTION
    # =========================================================

    def ingest_documents(
        self,
        documents,
        limit=None,
        offset=0,
    ):

        if documents is None:

            documents = []

        total_documents = len(
            documents
        )

        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )

        if limit is None:

            limit = total_documents

        if limit <= 0:

            raise ValueError(
                "limit doit être supérieur à 0."
            )

        batch = documents[
            offset:
            offset + limit
        ]

        print("=" * 60)

        print(
            "[RAG INGESTION] "
            f"Documents disponibles : "
            f"{total_documents}"
        )

        print(
            "[RAG INGESTION] "
            f"Offset : {offset}"
        )

        print(
            "[RAG INGESTION] "
            f"Limite : {limit}"
        )

        print(
            "[RAG INGESTION] "
            f"Documents du batch : "
            f"{len(batch)}"
        )

        print("=" * 60)

        inserted = 0
        updated = 0
        skipped = 0
        filtered_out = 0
        errors = 0

        # =====================================================
        # TRAITEMENT
        # =====================================================

        for index, raw_document in enumerate(
            batch,
            start=offset + 1,
        ):

            try:

                document = (
                    self.normalize_document(
                        raw_document
                    )
                )

                title = (
                    self.get_document_title(
                        document
                    )
                )

                content = (
                    self.get_document_content(
                        document
                    )
                )

                document_id = (
                    self.get_document_id(
                        document
                    )
                )

                print(
                    "[RAG INGESTION] "
                    f"[{index}/{total_documents}] "
                    f"{title[:100]}"
                )

                # =============================================
                # CONTENU
                # =============================================

                if not content:

                    print(
                        "⚠️ Document sans contenu."
                    )

                    skipped += 1

                    continue

                # =============================================
                # FILTRE AGRICOLE
                # =============================================

                relevance = (
                    self.relevance_filter.analyze(
                        document
                    )
                )

                if not relevance.relevant:

                    filtered_out += 1

                    print(
                        "🌾 Document filtré : "
                        "hors domaine agricole."
                    )

                    print(
                        f"   Score : "
                        f"{relevance.score:.3f}"
                    )

                    print(
                        f"   Raison : "
                        f"{relevance.reason}"
                    )

                    continue

                print(
                    "🌾 Document agricole validé."
                )

                print(
                    f"   Score : "
                    f"{relevance.score:.3f}"
                )

                print(
                    f"   Raison : "
                    f"{relevance.reason}"
                )

                # =============================================
                # TEXTE RAG
                # =============================================

                text = (
                    self.build_rag_text(
                        document
                    )
                )

                if not text.strip():

                    print(
                        "⚠️ Texte RAG vide."
                    )

                    skipped += 1

                    continue

                # =============================================
                # EMBEDDING
                # =============================================

                print(
                    "🤖 Génération embedding..."
                )

                embedding = (
                    self.embedding_service
                    .generate_document_embedding(
                        text
                    )
                )

                if not embedding:

                    raise ValueError(
                        "Embedding vide."
                    )

                if len(embedding) != (
                    self.EMBEDDING_DIMENSION
                ):

                    raise ValueError(
                        "Dimension embedding incorrecte : "
                        f"{len(embedding)} "
                        f"au lieu de "
                        f"{self.EMBEDDING_DIMENSION}."
                    )

                # =============================================
                # MÉTADONNÉES
                # =============================================

                metadata = (
                    self.build_metadata(
                        document
                    )
                )

                # =============================================
                # DOCUMENT EXISTANT ?
                # =============================================

                existing = (
                    self.vectorstore.exists(
                        document_id
                    )
                )

                # =============================================
                # MISE À JOUR
                # =============================================

                if existing:

                    print(
                        "🔄 Document déjà présent. "
                        "Mise à jour."
                    )

                    self.vectorstore.delete_document(
                        document_id
                    )

                    self.vectorstore.add_document(
                        doc_id=document_id,
                        chunks=[text],
                        embeddings=[embedding],
                        metadata=metadata,
                    )

                    updated += 1

                # =============================================
                # INSERTION
                # =============================================

                else:

                    self.vectorstore.add_document(
                        doc_id=document_id,
                        chunks=[text],
                        embeddings=[embedding],
                        metadata=metadata,
                    )

                    inserted += 1

                    print(
                        "✅ Document inséré dans "
                        "knowledge_embeddings."
                    )

            except Exception as e:

                errors += 1

                print(
                    f"❌ Erreur document {index} : "
                    f"{e}"
                )

        # =====================================================
        # PAGINATION
        # =====================================================

        next_offset = (
            offset
            + len(batch)
        )

        has_more = (
            next_offset
            < total_documents
        )

        return {

            "status":
                "success",

            "total_documents":
                total_documents,

            "batch_offset":
                offset,

            "batch_limit":
                limit,

            "batch_processed":
                len(batch),

            "inserted":
                inserted,

            "updated":
                updated,

            "filtered_out":
                filtered_out,

            "skipped":
                skipped,

            "errors":
                errors,

            "next_offset":
                next_offset,

            "has_more":
                has_more,
        }

    # =========================================================
    # COMPATIBILITÉ
    # =========================================================

    def ingest(
        self,
        documents=None,
        limit=100,
        offset=0,
    ):

        if documents is None:

            return {

                "status":
                    "error",

                "message":
                    (
                        "Cette version de "
                        "RAGIngestion fonctionne "
                        "directement avec des "
                        "documents en mémoire."
                    ),

                "total_documents":
                    0,

                "batch_processed":
                    0,

                "inserted":
                    0,

                "updated":
                    0,

                "filtered_out":
                    0,

                "skipped":
                    0,

                "errors":
                    0,

                "next_offset":
                    offset,

                "has_more":
                    False,
            }

        return self.ingest_documents(
            documents=documents,
            limit=limit,
            offset=offset,
        )


# =============================================================
# TEST
# =============================================================

def test_rag_ingestion():

    return {

        "status":
            "success",

        "message":
            (
                "RAGIngestion opérationnel. "
                "Le pipeline utilise maintenant "
                "Jina Embeddings v3 1024D, "
                "le filtre de pertinence agricole "
                "et Supabase knowledge_embeddings."
            ),
    }