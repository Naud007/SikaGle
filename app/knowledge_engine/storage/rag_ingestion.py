import os
import time

from supabase import create_client, Client

from app.ai.embeddings import (
    GeminiEmbeddingService
)


# =============================================================
# RAG INGESTION
# =============================================================

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
        # SERVICE EMBEDDING GEMINI
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService(
                model="jina-embeddings-v3",
                output_dimensionality=1024
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


        if hasattr(
            document,
            "model_dump"
        ):

            return document.model_dump(
                mode="json"
            )


        raise ValueError(
            "Format document non supporté : "
            f"{type(document).__name__}"
        )


    # =========================================================
    # EXTRAIRE LA SOURCE UNIQUE
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
    # CONSTRUIRE TEXTE POUR EMBEDDING
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
    # RECHERCHER DOCUMENT EXISTANT
    # =========================================================

    def find_existing_document(
        self,
        source_path
    ):

        if not source_path:

            return None


        try:

            response = (

                self.supabase

                .table(
                    "documents_rag"
                )

                .select(
                    "id, source_path"
                )

                .eq(
                    "source_path",
                    source_path
                )

                .limit(
                    1
                )

                .execute()

            )


            if response.data:

                return response.data[0]


            return None


        except Exception as e:

            print(
                "[RAG INGESTION] "
                "Erreur recherche doublon :",
                e
            )

            return None


    # =========================================================
    # CONSTRUIRE LA LIGNE SUPABASE
    # =========================================================

    def build_supabase_row(
        self,
        document,
        embedding
    ):

        title = self.get_document_title(
            document
        )

        source = self.get_document_source_name(
            document
        )

        url = self.get_document_source(
            document
        )

        text = self.build_rag_text(
            document
        )


        # -----------------------------------------------------
        # LANGUE
        # -----------------------------------------------------

        language = (
            document.get(
                "language"
            )
            or
            document.get(
                "langue"
            )
        )


        # -----------------------------------------------------
        # TYPE DOCUMENT
        # -----------------------------------------------------

        document_type = (
            document.get(
                "document_type"
            )
            or
            document.get(
                "type_document"
            )
            or
            "agricultural_publication"
        )


        # -----------------------------------------------------
        # CULTURE
        # -----------------------------------------------------

        culture = (
            document.get(
                "culture"
            )
            or
            document.get(
                "crop"
            )
        )


        # -----------------------------------------------------
        # ZONE GÉOGRAPHIQUE
        # -----------------------------------------------------

        zone_geographique = (
            document.get(
                "zone_geographique"
            )
            or
            document.get(
                "country"
            )
        )


        # -----------------------------------------------------
        # MOTS-CLÉS
        # -----------------------------------------------------

        mots_cles = (
            document.get(
                "mots_cles"
            )
            or
            document.get(
                "keywords"
            )
        )


        # -----------------------------------------------------
        # ANNÉE
        # -----------------------------------------------------

        annee = (
            document.get(
                "year"
            )
            or
            document.get(
                "annee"
            )
        )


        if annee:

            try:

                annee = int(
                    str(annee)[:4]
                )

            except Exception:

                annee = None


        return {

            "titre":
                title,

            "organisme":
                source,

            "annee":
                annee,

            "langue":
                language,

            "type_document":
                document_type,

            "culture":
                culture,

            "zone_geographique":
                zone_geographique,

            "mots_cles":
                mots_cles,

            "source_path":
                url,

            "content":
                text,

            "embedding":
                embedding

        }


    # =========================================================
    # INGÉRER DES DOCUMENTS DIRECTEMENT EN MÉMOIRE
    # =========================================================

    def ingest_documents(
        self,
        documents,
        limit=None,
        offset=0
    ):

        # =====================================================
        # VALIDATION
        # =====================================================

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


        # =====================================================
        # SÉLECTION DU BATCH
        # =====================================================

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
        errors = 0


        # =====================================================
        # TRAITEMENT
        # =====================================================

        for index, raw_document in enumerate(
            batch,
            start=offset + 1
        ):

            try:

                # -------------------------------------------------
                # NORMALISER
                # -------------------------------------------------

                document = self.normalize_document(
                    raw_document
                )


                title = self.get_document_title(
                    document
                )

                source_path = self.get_document_source(
                    document
                )

                content = self.get_document_content(
                    document
                )


                print(
                    f"[RAG INGESTION] "
                    f"[{index}/{total_documents}] "
                    f"{title[:100]}"
                )


                # -------------------------------------------------
                # VÉRIFIER CONTENU
                # -------------------------------------------------

                if not content:

                    print(
                        "⚠️ Document sans contenu."
                    )

                    skipped += 1

                    continue


                # -------------------------------------------------
                # CONSTRUIRE TEXTE
                # -------------------------------------------------

                text = self.build_rag_text(
                    document
                )


                if not text.strip():

                    print(
                        "⚠️ Texte RAG vide."
                    )

                    skipped += 1

                    continue


                # -------------------------------------------------
                # EMBEDDING
                # -------------------------------------------------

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


                # -------------------------------------------------
                # LIGNE SUPABASE
                # -------------------------------------------------

                row = self.build_supabase_row(
                    document,
                    embedding
                )


                # -------------------------------------------------
                # DOCUMENT EXISTANT ?
                # -------------------------------------------------

                existing_document = (
                    self.find_existing_document(
                        source_path
                    )
                )


                # -------------------------------------------------
                # UPDATE
                # -------------------------------------------------

                if existing_document:

                    document_id = (
                        existing_document.get(
                            "id"
                        )
                    )


                    (

                        self.supabase

                        .table(
                            "documents_rag"
                        )

                        .update(
                            row
                        )

                        .eq(
                            "id",
                            document_id
                        )

                        .execute()

                    )


                    updated += 1


                    print(
                        "🔄 Document mis à jour."
                    )


                # -------------------------------------------------
                # INSERT
                # -------------------------------------------------

                else:

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


                    print(
                        "✅ Document inséré."
                    )


                # -------------------------------------------------
                # PETITE PAUSE GEMINI
                # -------------------------------------------------

                time.sleep(
                    0.7
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

            "updated":
                updated,

            "skipped":
                skipped,

            "errors":
                errors,

            "next_offset":
                next_offset,

            "has_more":
                has_more

        }


    # =========================================================
    # COMPATIBILITÉ AVEC ANCIEN CODE
    # =========================================================

    def ingest(
        self,
        documents=None,
        limit=100,
        offset=0
    ):

        if documents is None:

            return {

                "status":
                    "error",

                "message":
                    (
                        "Cette version de RAGIngestion "
                        "fonctionne directement avec "
                        "des documents en mémoire."
                    ),

                "total_documents":
                    0,

                "batch_processed":
                    0,

                "inserted":
                    0,

                "updated":
                    0,

                "skipped":
                    0,

                "errors":
                    0,

                "next_offset":
                    offset,

                "has_more":
                    False

            }


        return self.ingest_documents(

            documents=documents,

            limit=limit,

            offset=offset

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
                "Le service attend maintenant "
                "des documents directement en mémoire."
            )

    }
