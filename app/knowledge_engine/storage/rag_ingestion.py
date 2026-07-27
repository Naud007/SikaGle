import os
import time

from supabase import create_client, Client

from app.ai.embeddings import (
    GeminiEmbeddingService
)


class RAGIngestion:

    def __init__(self):

        # =====================================================
        # CONFIGURATION SUPABASE
        # =====================================================

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

        self.supabase: Client = create_client(
            supabase_url,
            supabase_key
        )

        # =====================================================
        # SERVICE EMBEDDING GEMINI
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService(
                model="gemini-embedding-001",
                output_dimensionality=1536
            )
        )

    # =========================================================
    # CONVERTIR UN DOCUMENT EN DICTIONNAIRE
    # =========================================================

    def normalize_document(
        self,
        document
    ):

        if isinstance(
            document,
            dict
        ):
            return document

        # Pydantic v2
        if hasattr(
            document,
            "model_dump"
        ):
            return document.model_dump(
                mode="json"
            )

        # Pydantic v1
        if hasattr(
            document,
            "dict"
        ):
            return document.dict()

        raise ValueError(
            "Format de document non supporté."
        )

    # =========================================================
    # RÉCUPÉRER LES SOURCES DÉJÀ INGÉRÉES
    # =========================================================

    def get_existing_sources(
        self
    ):

        try:

            response = (
                self.supabase
                .table(
                    "documents_rag"
                )
                .select(
                    "source_path"
                )
                .execute()
            )

            existing_sources = set()

            for row in (
                response.data
                or []
            ):

                source_path = row.get(
                    "source_path"
                )

                if source_path:

                    existing_sources.add(
                        str(
                            source_path
                        ).strip()
                    )

            print(
                "[RAG INGESTION] "
                f"{len(existing_sources)} "
                "source(s) déjà présente(s) "
                "dans Supabase."
            )

            return existing_sources

        except Exception as e:

            print(
                "[RAG INGESTION] "
                "Erreur récupération "
                "des sources existantes :",
                e
            )

            return set()

    # =========================================================
    # EXTRAIRE LA SOURCE / URL
    # =========================================================

    def get_document_source(
        self,
        document
    ):

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
    # EXTRAIRE LE TITRE
    # =========================================================

    def get_document_title(
        self,
        document
    ):

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
    # EXTRAIRE LE CONTENU
    # =========================================================

    def get_document_content(
        self,
        document
    ):

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
    # EXTRAIRE ORGANISME / SOURCE
    # =========================================================

    def get_document_source_name(
        self,
        document
    ):

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
    # CONSTRUIRE LE TEXTE POUR LE RAG
    # =========================================================

    def build_rag_text(
        self,
        document
    ):

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

        parts = [
            f"Titre : {title}"
        ]

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
    # INGÉRER DIRECTEMENT UNE LISTE DE DOCUMENTS
    # =========================================================

    def ingest_documents(
        self,
        documents,
        limit=None
    ):

        if documents is None:

            raise ValueError(
                "Aucun document fourni."
            )

        documents = list(
            documents
        )

        total_documents = len(
            documents
        )

        print(
            "[RAG INGESTION] "
            f"{total_documents} document(s) "
            "reçu(s) directement en mémoire."
        )

        if limit is not None:

            if limit <= 0:
                raise ValueError(
                    "limit doit être supérieur à 0."
                )

            documents = documents[
                :limit
            ]

        if not documents:

            return {
                "status": "success",
                "message": (
                    "Aucun document à ingérer."
                ),
                "total_documents": 0,
                "processed": 0,
                "inserted": 0,
                "skipped": 0,
                "errors": 0
            }

        existing_sources = (
            self.get_existing_sources()
        )

        inserted = 0
        skipped = 0
        errors = 0

        # =====================================================
        # TRAITEMENT
        # =====================================================

        for index, raw_document in enumerate(
            documents,
            start=1
        ):

            try:

                # -------------------------------------------------
                # NORMALISATION
                # -------------------------------------------------

                document = (
                    self.normalize_document(
                        raw_document
                    )
                )

                # -------------------------------------------------
                # MÉTADONNÉES
                # -------------------------------------------------

                title = (
                    self.get_document_title(
                        document
                    )
                )

                source = (
                    self.get_document_source_name(
                        document
                    )
                )

                url = (
                    self.get_document_source(
                        document
                    )
                )

                content = (
                    self.get_document_content(
                        document
                    )
                )

                # -------------------------------------------------
                # VÉRIFICATION CONTENU
                # -------------------------------------------------

                if not content:

                    print(
                        f"⚠️ [{index}] "
                        "Document sans contenu : "
                        f"{title}"
                    )

                    errors += 1
                    continue

                # -------------------------------------------------
                # VÉRIFICATION DOUBLON
                # -------------------------------------------------

                if (
                    url
                    and url in existing_sources
                ):

                    print(
                        f"⏭️ [{index}] "
                        "Déjà présent : "
                        f"{title[:80]}"
                    )

                    skipped += 1
                    continue

                # -------------------------------------------------
                # CONSTRUIRE TEXTE RAG
                # -------------------------------------------------

                text = (
                    self.build_rag_text(
                        document
                    )
                )

                print(
                    f"🤖 [{index}] "
                    "Embedding : "
                    f"{title[:80]}"
                )

                # -------------------------------------------------
                # EMBEDDING GEMINI
                # -------------------------------------------------

                embedding = (
                    self.embedding_service
                    .generate_document_embedding(
                        text
                    )
                )

                if not embedding:

                    print(
                        f"❌ [{index}] "
                        "Embedding vide."
                    )

                    errors += 1
                    continue

                # -------------------------------------------------
                # MOTS-CLÉS
                # -------------------------------------------------

                keywords = (
                    document.get(
                        "keywords"
                    )
                    or document.get(
                        "mots_cles"
                    )
                )

                # -------------------------------------------------
                # ANNÉE
                # -------------------------------------------------

                year = (
                    document.get(
                        "year"
                    )
                    or document.get(
                        "annee"
                    )
                )

                # -------------------------------------------------
                # LIGNE SUPABASE
                # -------------------------------------------------

                row = {

                    "titre":
                        title,

                    "organisme":
                        source,

                    "annee":
                        year,

                    "langue":
                        (
                            document.get(
                                "language"
                            )
                            or document.get(
                                "langue"
                            )
                            or "fr"
                        ),

                    "type_document":
                        (
                            document.get(
                                "document_type"
                            )
                            or document.get(
                                "type_document"
                            )
                            or "agricultural_document"
                        ),

                    "culture":
                        (
                            document.get(
                                "crop"
                            )
                            or document.get(
                                "culture"
                            )
                        ),

                    "zone_geographique":
                        (
                            document.get(
                                "country"
                            )
                            or document.get(
                                "zone_geographique"
                            )
                        ),

                    "mots_cles":
                        keywords,

                    "source_path":
                        url,

                    "content":
                        text,

                    "embedding":
                        embedding
                }

                # -------------------------------------------------
                # RETIRER LES VALEURS NONE FACULTATIVES
                # -------------------------------------------------

                optional_fields = [
                    "annee",
                    "culture",
                    "zone_geographique",
                    "mots_cles",
                ]

                for field in optional_fields:

                    if row.get(
                        field
                    ) is None:

                        row.pop(
                            field,
                            None
                        )

                # -------------------------------------------------
                # INSERTION SUPABASE
                # -------------------------------------------------

                (
                    self.supabase
                    .table(
                        "documents_rag"
                    )
                    .insert(
                        row
                    )
                    .execute()
                )

                inserted += 1

                if url:
                    existing_sources.add(
                        url
                    )

                print(
                    f"✅ [{index}] "
                    "Document inséré : "
                    f"{title[:80]}"
                )

                # -------------------------------------------------
                # PAUSE GEMINI
                # -------------------------------------------------

                time.sleep(
                    0.7
                )

            except Exception as e:

                errors += 1

                print(
                    f"❌ [{index}] "
                    "Erreur ingestion : "
                    f"{e}"
                )

        # =====================================================
        # RÉSULTAT
        # =====================================================

        return {

            "status":
                "success",

            "total_documents":
                total_documents,

            "processed":
                len(
                    documents
                ),

            "inserted":
                inserted,

            "skipped":
                skipped,

            "errors":
                errors
        }


# =============================================================
# TEST SIMPLE DU SERVICE
# =============================================================

def test_rag_ingestion():

    return {

        "status":
            "success",

        "message":
            (
                "RAGIngestion prêt. "
                "Utilisez ingest_documents() "
                "avec des documents parsés."
            )

    }
