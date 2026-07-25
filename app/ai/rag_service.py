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

        print(
            "✅ Connexion Supabase initialisée."
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

            existing_sources = {

                str(
                    row.get(
                        "source_path"
                    )
                )

                for row in (
                    response.data
                    or []
                )

                if row.get(
                    "source_path"
                )

            }

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
    # CONSTRUIRE LE TEXTE RAG
    # =========================================================

    def build_rag_text(
        self,
        document
    ):

        # -------------------------------------------------
        # 1. UTILISER LE CONTENT EXISTANT
        # -------------------------------------------------

        content = (

            document.get(
                "content"
            )

            or ""

        )

        content = str(
            content
        ).strip()


        # -------------------------------------------------
        # 2. RÉCUPÉRER LES MÉTADONNÉES
        # -------------------------------------------------

        title = (

            document.get(
                "title"
            )

            or ""

        )

        description = (

            document.get(
                "description"
            )

            or ""

        )

        source = (

            document.get(
                "source"
            )

            or "FAO AGRIS"

        )

        url = (

            document.get(
                "url"
            )

            or ""

        )


        # -------------------------------------------------
        # 3. SI CONTENT EXISTE
        #    ON L'UTILISE COMME TEXTE PRINCIPAL
        # -------------------------------------------------

        if content:

            return content


        # -------------------------------------------------
        # 4. FALLBACK
        #    SI CONTENT EST VIDE
        # -------------------------------------------------

        content_parts = []


        if title:

            content_parts.append(

                f"Titre : "
                f"{title}"

            )


        if description:

            content_parts.append(

                f"Description : "
                f"{description}"

            )


        if source:

            content_parts.append(

                f"Source : "
                f"{source}"

            )


        if url:

            content_parts.append(

                f"URL : "
                f"{url}"

            )


        # -------------------------------------------------
        # 5. DERNIER FALLBACK
        # -------------------------------------------------

        if not content_parts:

            return (
                "Document FAO AGRIS "
                "sans contenu exploitable."
            )


        return "\n\n".join(
            content_parts
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
        # CHARGER LES DOCUMENTS LOCAUX
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
        # TRAITEMENT DES DOCUMENTS
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

                    document.get(
                        "title"
                    )

                    or "Document sans titre"

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
                # VÉRIFICATION DOUBLON
                # -------------------------------------------------

                if (

                    url

                    and

                    str(url)
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
                # CONSTRUIRE LE CONTENU RAG
                # -------------------------------------------------

                text = self.build_rag_text(
                    document
                )


                # -------------------------------------------------
                # VÉRIFIER LE CONTENU
                # -------------------------------------------------

                if not text.strip():

                    print(

                        f"⚠️ [{index}] "
                        f"Contenu vide : "
                        f"{title[:80]}"

                    )

                    skipped += 1

                    continue


                print(

                    f"📄 [{index}] "
                    f"Contenu : "
                    f"{len(text)} caractères"

                )


                print(

                    f"🤖 [{index}] "
                    f"Embedding : "
                    f"{title[:80]}"

                )


                # -------------------------------------------------
                # GÉNÉRATION EMBEDDING
                # -------------------------------------------------

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

                    "version":
                        document.get(
                            "version"
                        ),

                    "annee":
                        document.get(
                            "year"
                        ),

                    "langue":
                        document.get(
                            "language"
                        ),

                    "type_document":
                        document.get(
                            "document_type"
                        ),

                    "culture":
                        document.get(
                            "crop"
                        ),

                    "zone_geographique":
                        document.get(
                            "country"
                        ),

                    "mots_cles":
                        document.get(
                            "keywords"
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
                        str(url)
                    )


                print(

                    f"✅ [{index}] "
                    f"Document inséré : "
                    f"{title[:80]}"

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
                len(batch),

            "inserted":
                inserted,

            "skipped":
                skipped,

            "errors":
                errors,

            "next_offset":
                offset + len(batch)

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
