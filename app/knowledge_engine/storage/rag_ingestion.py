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
        # SERVICE EMBEDDING GEMINI
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
                "sources existantes :",

                e

            )

            return set()


    # =========================================================
    # EXTRAIRE LA SOURCE DU DOCUMENT
    # =========================================================

    def get_document_source(
        self,
        document
    ):

        # -----------------------------------------------------
        # URL DU PARSER
        # -----------------------------------------------------

        url = document.get(
            "url"
        )


        if url:

            return str(
                url
            ).strip()


        # -----------------------------------------------------
        # SOURCE_PATH
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

        # -----------------------------------------------------
        # FORMAT PARSER FAO
        # -----------------------------------------------------

        title = document.get(
            "title"
        )


        if title:

            return str(
                title
            ).strip()


        # -----------------------------------------------------
        # FORMAT SUPABASE
        # -----------------------------------------------------

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
    # EXTRAIRE LE CONTENU COMPLET
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


        # -----------------------------------------------------
        # FALLBACK DESCRIPTION
        # -----------------------------------------------------

        description = document.get(
            "description"
        )


        if description:

            return str(
                description
            ).strip()


        return ""


    # =========================================================
    # EXTRAIRE LA SOURCE / ORGANISME
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
    # CONSTRUIRE LE TEXTE RAG
    # =========================================================

    def build_rag_text(
        self,
        document
    ):

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


        parts = []


        # -----------------------------------------------------
        # TITRE
        # -----------------------------------------------------

        parts.append(

            f"Titre : {title}"

        )


        # -----------------------------------------------------
        # CONTENU
        # -----------------------------------------------------

        if content:

            parts.append(

                f"Contenu :\n{content}"

            )


        # -----------------------------------------------------
        # SOURCE
        # -----------------------------------------------------

        if source:

            parts.append(

                f"Source : {source}"

            )


        # -----------------------------------------------------
        # URL
        # -----------------------------------------------------

        if url:

            parts.append(

                f"URL : {url}"

            )


        return "\n\n".join(
            parts
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
        # VALIDATION
        # =====================================================

        if limit <= 0:

            raise ValueError(

                "limit doit être "
                "supérieur à 0."

            )


        if offset < 0:

            raise ValueError(

                "offset ne peut pas "
                "être négatif."

            )


        # =====================================================
        # CHARGER DOCUMENTS DEPUIS documents.json
        # =====================================================

        print(

            "[RAG INGESTION] "

            "Chargement des documents "
            "depuis le stockage local..."

        )


        all_documents = (

            self.document_store._load()

        )


        total_documents = (

            len(
                all_documents
            )

        )


        print(

            "[RAG INGESTION] "

            f"{total_documents} "
            "document(s) disponible(s) "
            "dans documents.json."

        )


        # =====================================================
        # AUCUN DOCUMENT
        # =====================================================

        if total_documents == 0:

            print(

                "[RAG INGESTION] "

                "Aucun document à ingérer."

            )


            return {

                "status":
                    "success",

                "message":
                    "Aucun document disponible "
                    "dans documents.json.",

                "total_documents":
                    0,

                "batch_offset":
                    offset,

                "batch_limit":
                    limit,

                "batch_processed":
                    0,

                "inserted":
                    0,

                "skipped":
                    0,

                "errors":
                    0,

                "next_offset":
                    offset

            }


        # =====================================================
        # SOURCES DÉJÀ PRÉSENTES DANS SUPABASE
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

            "[RAG INGESTION] "

            f"Batch sélectionné : "

            f"{offset} → "

            f"{offset + len(batch)}"

        )


        inserted = 0

        skipped = 0

        errors = 0


        # =====================================================
        # TRAITEMENT DES DOCUMENTS
        # =====================================================

        for index, document in enumerate(

            batch,

            start=offset + 1

        ):

            try:

                # -------------------------------------------------
                # VÉRIFIER FORMAT DOCUMENT
                # -------------------------------------------------

                if not isinstance(
                    document,
                    dict
                ):

                    print(

                        f"❌ [{index}] "

                        "Format document invalide."

                    )

                    errors += 1

                    continue


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
                # VÉRIFIER LE CONTENU
                # -------------------------------------------------

                if not content:

                    print(

                        f"⚠️ [{index}] "

                        f"Document sans contenu : "

                        f"{title}"

                    )

                    errors += 1

                    continue


                # -------------------------------------------------
                # VÉRIFIER LES DOUBLONS
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
                # CONSTRUIRE TEXTE RAG
                # -------------------------------------------------

                text = (

                    self.build_rag_text(
                        document
                    )

                )


                print(

                    f"🤖 [{index}] "

                    f"Embedding : "

                    f"{title[:80]}"

                )


                # -------------------------------------------------
                # GÉNÉRER EMBEDDING
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
                # CONSTRUIRE LIGNE SUPABASE
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
                            "langue"
                        )

                        or

                        "fr",


                    "type_document":

                        document.get(
                            "document_type"
                        )

                        or

                        document.get(
                            "type_document"
                        )

                        or

                        "technical_sheet",


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
                            "zone_geographique"
                        )

                        or

                        "Bénin",


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


                # -------------------------------------------------
                # SUCCÈS
                # -------------------------------------------------

                inserted += 1


                if url:

                    existing_sources.add(
                        url
                    )


                print(

                    f"✅ [{index}] "

                    f"Document inséré : "

                    f"{title[:80]}"

                )


                # -------------------------------------------------
                # PAUSE ENTRE LES REQUÊTES GEMINI
                # -------------------------------------------------

                time.sleep(
                    0.7
                )


            except Exception as e:

                errors += 1


                print(

                    f"❌ [{index}] "

                    f"Erreur ingestion : "

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
                str(
                    e
                )

        }
