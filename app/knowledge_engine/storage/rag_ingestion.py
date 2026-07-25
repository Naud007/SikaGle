import os
import time

from supabase import create_client, Client

from app.knowledge_engine.storage.document_store import (
    DocumentStore
)

from app.ai.embeddings import (
    GeminiEmbeddingService
)


class RAGIngestion:

    def __init__(self):

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

        self.document_store = (
            DocumentStore()
        )

        self.embedding_service = (
            GeminiEmbeddingService(
                model="gemini-embedding-001",
                output_dimensionality=1536
            )
        )


    # =========================================================
    # INGESTION
    # =========================================================

    def ingest(
        self,
        limit=100
    ):

        documents = (
            self.document_store
            .get_all()
        )

        print(
            f"[RAG INGESTION] "
            f"{len(documents)} documents trouvés."
        )

        documents = documents[:limit]

        inserted = 0
        skipped = 0
        errors = 0

        for index, document in enumerate(
            documents,
            start=1
        ):

            try:

                title = (
                    document.get(
                        "title"
                    )
                    or "Document sans titre"
                )

                description = (
                    document.get(
                        "description"
                    )
                    or ""
                )

                url = (
                    document.get(
                        "url"
                    )
                )

                source = (
                    document.get(
                        "source"
                    )
                    or "FAO AGRIS"
                )

                # -------------------------------------------------
                # TEXTE POUR EMBEDDING
                # -------------------------------------------------

                text = (
                    f"Titre : {title}\n\n"
                    f"Description : {description}\n\n"
                    f"Source : {source}"
                )

                print(
                    f"[{index}/{len(documents)}] "
                    f"Embedding : {title[:80]}"
                )

                # -------------------------------------------------
                # EMBEDDING
                # -------------------------------------------------

                embedding = (
                    self.embedding_service
                    .generate_document_embedding(
                        text
                    )
                )

                # -------------------------------------------------
                # DONNÉES SUPABASE
                # -------------------------------------------------

                row = {

                    "titre":
                        title,

                    "organisme":
                        source,

                    "langue":
                        document.get(
                            "language",
                            "fr"
                        ),

                    "type_document":
                        document.get(
                            "document_type",
                            "technical_sheet"
                        ),

                    "culture":
                        document.get(
                            "crop"
                        ),

                    "zone_geographique":
                        document.get(
                            "country",
                            "Bénin"
                        ),

                    "source_path":
                        str(url)
                        if url
                        else None,

                    "content":
                        text,

                    "embedding":
                        embedding

                }

                # -------------------------------------------------
                # INSERTION
                # -------------------------------------------------

                self.supabase \
                    .table(
                        "documents_rag"
                    ) \
                    .insert(
                        row
                    ) \
                    .execute()

                inserted += 1

                print(
                    "✅ Document inséré."
                )

                # -------------------------------------------------
                # PAUSE API
                # -------------------------------------------------

                time.sleep(
                    0.2
                )

            except Exception as e:

                errors += 1

                print(
                    f"❌ Erreur document "
                    f"{index} : {e}"
                )

        return {

            "status":
                "success",

            "documents_source":
                len(documents),

            "inserted":
                inserted,

            "skipped":
                skipped,

            "errors":
                errors

        }


# =========================================================
# TEST
# =========================================================

def test_rag_ingestion():

    try:

        ingestion = (
            RAGIngestion()
        )

        return ingestion.ingest(
            limit=10
        )

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
