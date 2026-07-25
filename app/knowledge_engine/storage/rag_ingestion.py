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

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key
            )
        )

        # =====================================================
        # DOCUMENT STORE
        # =====================================================

        self.document_store = (
            DocumentStore()
        )

        # =====================================================
        # SERVICE EMBEDDING
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService(
                model="gemini-embedding-001",
                output_dimensionality=1536
            )
        )


    # =========================================================
    # RÉCUPÉRER LES SOURCES DÉJÀ INGÉRÉES
    # =========================================================

    def get_existing_sources(self):

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

                source_path = (
                    row.get(
                        "source_path"
                    )
                )

                if source_path:

                    existing_sources.add(
                        str(
                            source_path
                        ).strip()
                    )

            print(

                f"[RAG INGESTION] "

                f"{len(existing_sources)} "
                f"document(s) déjà présents "
                f"dans documents_rag."

            )

            return existing_sources

        except Exception as e:

            print(

                "[RAG INGESTION] "
                "Erreur récupération documents existants :",

                e

            )

            return set()


    # =========================================================
    # RÉCUPÉRER L'URL / SOURCE DU DOCUMENT
    # =========================================================

    def get_document_source(
        self,
        document
    ):

        # -----------------------------------------------------
        # DOCUMENT LOCAL / FAO PARSER
        # -----------------------------------------------------

        url = document.get(
            "url"
        )

        if url:

            return str(
                url
            ).strip()


        # -----------------------------------------------------
        # DOCUMENT DÉJÀ STOCKÉ DANS SUPABASE
        # -----------------------------------------------------

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


        return (
            "Document sans titre"
        )


    # =========================================================
    # EXTRAIRE LA DESCRIPTION
    # =========================================================

    def get_document_description(
        self,
        document
    ):

        description = document.get(
            "description"
        )

        if description:

            return str(
                description
            ).strip()


        content = document.get(
            "content"
        )

        if content:

            return str(
                content
            ).strip()


        return ""


    # =========================================================
    # EXTRAIRE LA SOURCE
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


        return (
            "FAO AGRIS"
        )


    # =========================================================
    # INGESTION PAR LOT
    # =========================================================

    def ingest(
        self,
        limit=100,
        offset=0
    ):

        # =====================================================
        # VALIDATION PARAMÈTRES
        # =====================================================

        if limit <= 0:

            raise ValueError(
                "limit doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )


        # =====================================================
        # CHARGER DOCUMENTS
        # =====================================================

        all_documents = (
            self.document_store
            .get_all()
        )

        total_documents = (
            len(
                all_documents
            )
        )

        print(

            f"[RAG INGESTION] "

            f"{total_documents} "
            f"documents disponibles."

        )


        # =====================================================
        # RÉCUPÉRER LES DOCUMENTS DÉJÀ INGÉRÉS
        # =====================================================

        existing_sources = (
            self.get_existing_sources()
        )


        # =====================================================
        # SÉLECTION DU BATCH
        # =====================================================

        batch = (

            all_documents[
                offset:
                offset + limit
            ]

        )

        print(

            f"[RAG INGESTION] "

            f"Batch : "
            f"{offset} → "
            f"{offset + len(batch)}"

        )


        inserted = 0

        skipped = 0

        errors = 0


        # =====================================================
        # TRAITEMENT
        # =====================================================

        for index, document in enumerate(

            batch,

            start=offset + 1

        ):

            try:

                # -------------------------------------------------
                # MÉTADONNÉES
                # -------------------------------------------------

                title = (
                    self.get_document_title(
                        document
                    )
                )

                description = (
                    self.get_document_description(
                        document
                    )
                )

                url = (
                    self.get_document_source(
                        document
                    )
                )

                source = (
                    self.get_document_source_name(
                        document
                    )
                )


                # -------------------------------------------------
                # VÉRIFICATION DOUBLON
                # -------------------------------------------------

                if (

                    url

                    and

                    url
                    in existing_sources

                ):

                    print(

                        f"⏭️ [{index}] "
                        f"Déjà présent : "
                        f"{title[:80]}"

                    )

                    skipped += 1

                    continue


                # -------------------------------------------------
                # TEXTE RAG
                # -------------------------------------------------

                text = (

                    f"Titre : {title}\n\n"

                    f"Description : "
                    f"{description}\n\n"

                    f"Source : "
                    f"{source}"

                )


                # -------------------------------------------------
                # EMBEDDING
                # -------------------------------------------------

                print(

                    f"🤖 [{index}] "
                    f"Embedding : "
                    f"{title[:80]}"

                )

                embedding = (

                    self.embedding_service

                    .generate_document_embedding(

                        text

                    )

                )


                # -------------------------------------------------
                # CONSTRUCTION LIGNE SUPABASE
                # -------------------------------------------------

                row = {

                    "titre":
                        title,

                    "organisme":
                        source,

                    "langue":
                        document.get(
                            "language"
                        )
                        or
                        document.get(
                            "langue",
                            "fr"
                        ),

                    "type_document":
                        document.get(
                            "document_type"
                        )
                        or
                        document.get(
                            "type_document",
                            "technical_sheet"
                        ),

                    "culture":
                        document.get(
                            "crop"
                        )
                        or
                        document.get(
                            "culture"
                        ),

                    "zone_geographique":
                        document.get(
                            "country"
                        )
                        or
                        document.get(
                            "zone_geographique",
                            "Bénin"
                        ),

                    "source_path":
                        url,

                    "content":
                        text,

                    "embedding":
                        embedding

                }


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


                # Ajouter immédiatement la source
                # à la liste des documents existants

                if url:

                    existing_sources.add(
                        url
                    )


                print(

                    f"✅ [{index}] "
                    f"Document inséré."

                )


                # -------------------------------------------------
                # PAUSE API
                # -------------------------------------------------

                time.sleep(
                    0.7
                )


            except Exception as e:

                errors += 1

                print(

                    f"❌ [{index}] "
                    f"Erreur : "
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

            "batch_offset":
                offset,

            "batch_limit":
                limit,

            "batch_processed":
                len(
                    batch
                ),

            "inserted":
                inserted,

            "skipped":
                skipped,

            "errors":
                errors,

            "next_offset":
                offset + len(
                    batch
                )

        }


# =============================================================
# TEST RAG INGESTION
# =============================================================

def test_rag_ingestion():

    try:

        ingestion = (
            RAGIngestion()
        )

        return (

            ingestion.ingest(

                limit=10,

                offset=0

            )

        )

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
