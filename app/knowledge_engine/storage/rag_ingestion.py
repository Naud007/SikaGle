import os
import time

from supabase import create_client, Client

from app.knowledge_engine.storage.document_store import (
    DocumentStore
)

from app.ai.embeddings import (
    GeminiEmbeddingService
)


# =========================================================
# RAG INGESTION
# =========================================================

class RAGIngestion:

    def __init__(self):

        # =====================================================
        # SUPABASE
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
        # Ancienne architecture, conservée temporairement
        # =====================================================

        self.document_store = (
            DocumentStore()
        )

        # =====================================================
        # EMBEDDINGS
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService(
                model="gemini-embedding-001",
                output_dimensionality=1536
            )
        )


    # =========================================================
    # CONVERTIR UN DOCUMENT EN DICT
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

        return None


    # =========================================================
    # SOURCE UNIQUE
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
    # TITRE
    # =========================================================

    def get_document_title(
        self,
        document
    ):

        title = (
            document.get("title")
            or
            document.get("titre")
        )

        if title:
            return str(
                title
            ).strip()

        return "Document sans titre"


    # =========================================================
    # CONTENU
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
    # ORGANISME
    # =========================================================

    def get_document_source_name(
        self,
        document
    ):

        source = (
            document.get("source")
            or
            document.get("organisme")
        )

        if source:
            return str(
                source
            ).strip()

        return "FAO AGRIS"


    # =========================================================
    # LANGUE
    # =========================================================

    def get_document_language(
        self,
        document
    ):

        language = (
            document.get("language")
            or
            document.get("langue")
        )

        if language:

            language = str(
                language
            ).strip().lower()

            language_map = {

                "english": "en",
                "eng": "en",
                "en": "en",

                "french": "fr",
                "fra": "fr",
                "fre": "fr",
                "fr": "fr",
                "français": "fr",

                "portuguese": "pt",
                "por": "pt",
                "pt": "pt",

                "spanish": "es",
                "spa": "es",
                "es": "es",
            }

            return language_map.get(
                language,
                language
            )

        # AGRIS contient beaucoup de publications anglaises.
        # Ce fallback sera amélioré plus tard si nécessaire.
        return "en"


    # =========================================================
    # CULTURE
    # =========================================================

    def get_document_crop(
        self,
        document
    ):

        crop = (
            document.get("crop")
            or
            document.get("culture")
        )

        if crop:
            return str(
                crop
            ).strip()

        return None


    # =========================================================
    # ZONE GÉOGRAPHIQUE
    # =========================================================

    def get_document_geography(
        self,
        document
    ):

        geography = (
            document.get(
                "zone_geographique"
            )
            or
            document.get(
                "country"
            )
        )

        if geography:
            return str(
                geography
            ).strip()

        return None


    # =========================================================
    # MOTS-CLÉS
    # =========================================================

    def get_document_keywords(
        self,
        document
    ):

        keywords = (
            document.get(
                "mots_cles"
            )
            or
            document.get(
                "keywords"
            )
        )

        if not keywords:
            return None

        if isinstance(
            keywords,
            list
        ):

            cleaned = []

            for keyword in keywords:

                if not keyword:
                    continue

                value = str(
                    keyword
                ).strip()

                if (
                    value
                    and value not in cleaned
                ):
                    cleaned.append(
                        value
                    )

            return (
                cleaned
                if cleaned
                else None
            )

        if isinstance(
            keywords,
            str
        ):

            cleaned = [

                value.strip()

                for value
                in keywords.split(",")

                if value.strip()

            ]

            return (
                cleaned
                if cleaned
                else None
            )

        return None


    # =========================================================
    # TYPE DOCUMENT
    # =========================================================

    def get_document_type(
        self,
        document
    ):

        document_type = (
            document.get(
                "document_type"
            )
            or
            document.get(
                "type_document"
            )
        )

        if document_type:
            return str(
                document_type
            ).strip()

        return "agricultural_publication"


    # =========================================================
    # TEXTE POUR EMBEDDING
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

        language = (
            self.get_document_language(
                document
            )
        )

        crop = (
            self.get_document_crop(
                document
            )
        )

        geography = (
            self.get_document_geography(
                document
            )
        )

        keywords = (
            self.get_document_keywords(
                document
            )
        )

        parts = []

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

        if language:
            parts.append(
                f"Langue : {language}"
            )

        if crop:
            parts.append(
                f"Culture : {crop}"
            )

        if geography:
            parts.append(
                "Zone géographique : "
                f"{geography}"
            )

        if keywords:
            parts.append(
                "Mots-clés : "
                + ", ".join(
                    keywords
                )
            )

        if url:
            parts.append(
                f"URL : {url}"
            )

        return "\n\n".join(
            parts
        )


    # =========================================================
    # RECHERCHER UN DOCUMENT EXISTANT PAR SOURCE
    # =========================================================

    def find_existing_document(
        self,
        source_path
    ):

        if not source_path:
            return None

        response = (

            self.supabase

            .table(
                "documents_rag"
            )

            .select(
                "id, "
                "titre, "
                "organisme, "
                "langue, "
                "type_document, "
                "culture, "
                "zone_geographique, "
                "mots_cles, "
                "source_path, "
                "content"
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


    # =========================================================
    # INGESTION DIRECTE DES DOCUMENTS
    #
    # NOUVELLE ARCHITECTURE
    # =========================================================

    def ingest_documents(
        self,
        documents,
        limit=20,
        offset=0
    ):

        # =====================================================
        # VALIDATION
        # =====================================================

        if documents is None:

            raise ValueError(
                "documents ne peut pas être None."
            )

        if limit <= 0:

            raise ValueError(
                "limit doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )


        total_documents = len(
            documents
        )


        print("=" * 60)

        print(
            "[RAG DIRECT] "
            f"{total_documents} document(s) reçu(s)."
        )

        print(
            "[RAG DIRECT] "
            f"Offset : {offset}"
        )

        print(
            "[RAG DIRECT] "
            f"Limit : {limit}"
        )

        print("=" * 60)


        # =====================================================
        # OFFSET TERMINÉ
        # =====================================================

        if offset >= total_documents:

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


        # =====================================================
        # SÉLECTION DU BATCH
        # =====================================================

        batch = (

            documents[

                offset:

                offset + limit

            ]

        )


        inserted = 0
        updated = 0
        skipped = 0
        errors = 0


        # =====================================================
        # TRAITEMENT
        # =====================================================

        for local_index, raw_document in enumerate(
            batch
        ):

            absolute_index = (
                offset
                + local_index
            )


            try:

                # =================================================
                # NORMALISATION
                # =================================================

                document = (
                    self.normalize_document(
                        raw_document
                    )
                )


                if not document:

                    print(
                        f"❌ [{absolute_index}] "
                        "Format document invalide."
                    )

                    errors += 1

                    continue


                # =================================================
                # MÉTADONNÉES
                # =================================================

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

                language = (
                    self.get_document_language(
                        document
                    )
                )

                crop = (
                    self.get_document_crop(
                        document
                    )
                )

                geography = (
                    self.get_document_geography(
                        document
                    )
                )

                keywords = (
                    self.get_document_keywords(
                        document
                    )
                )

                document_type = (
                    self.get_document_type(
                        document
                    )
                )


                # =================================================
                # SOURCE REQUISE
                # =================================================

                if not url:

                    print(
                        f"⚠️ [{absolute_index}] "
                        f"URL absente : {title}"
                    )

                    errors += 1

                    continue


                # =================================================
                # TEXTE RAG
                # =================================================

                rag_text = (
                    self.build_rag_text(
                        document
                    )
                )


                if not rag_text.strip():

                    print(
                        f"⚠️ [{absolute_index}] "
                        f"Contenu vide : {title}"
                    )

                    errors += 1

                    continue


                # =================================================
                # RECHERCHE EXISTANT
                # =================================================

                existing = (
                    self.find_existing_document(
                        url
                    )
                )


                # =================================================
                # DONNÉES SUPABASE
                # =================================================

                row = {

                    "titre":
                        title,

                    "organisme":
                        source,

                    "langue":
                        language,

                    "type_document":
                        document_type,

                    "culture":
                        crop,

                    "zone_geographique":
                        geography,

                    "mots_cles":
                        keywords,

                    "source_path":
                        url,

                    "content":
                        rag_text,

                }


                # =================================================
                # DOCUMENT EXISTANT
                # =================================================

                if existing:

                    existing_content = (
                        existing.get(
                            "content"
                        )
                        or ""
                    )


                    # =============================================
                    # CONTENU IDENTIQUE
                    # =============================================

                    if (
                        existing_content.strip()
                        ==
                        rag_text.strip()
                    ):

                        # Même si le contenu est identique,
                        # on met à jour les métadonnées.

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
                                existing["id"]
                            )

                            .execute()

                        )


                        updated += 1


                        print(
                            f"📝 [{absolute_index}] "
                            f"Métadonnées mises à jour : "
                            f"{title[:70]}"
                        )


                        continue


                    # =============================================
                    # CONTENU MODIFIÉ
                    # =============================================

                    print(
                        f"🔄 [{absolute_index}] "
                        f"Contenu modifié : "
                        f"{title[:70]}"
                    )


                    embedding = (

                        self.embedding_service

                        .generate_document_embedding(
                            rag_text
                        )

                    )


                    if not embedding:

                        errors += 1

                        print(
                            f"❌ [{absolute_index}] "
                            "Embedding vide."
                        )

                        continue


                    row[
                        "embedding"
                    ] = embedding


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
                            existing["id"]
                        )

                        .execute()

                    )


                    updated += 1


                    print(
                        f"✅ [{absolute_index}] "
                        f"Document actualisé : "
                        f"{title[:70]}"
                    )


                    time.sleep(
                        0.7
                    )


                    continue


                # =================================================
                # NOUVEAU DOCUMENT
                # =================================================

                print(
                    f"🤖 [{absolute_index}] "
                    f"Nouvel embedding : "
                    f"{title[:70]}"
                )


                embedding = (

                    self.embedding_service

                    .generate_document_embedding(
                        rag_text
                    )

                )


                if not embedding:

                    errors += 1

                    print(
                        f"❌ [{absolute_index}] "
                        "Embedding vide."
                    )

                    continue


                row[
                    "embedding"
                ] = embedding


                # =================================================
                # INSERTION
                # =================================================

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
                    f"✅ [{absolute_index}] "
                    f"Inséré : "
                    f"{title[:70]}"
                )


                time.sleep(
                    0.7
                )


            except Exception as e:

                errors += 1

                print(
                    f"❌ [{absolute_index}] "
                    f"Erreur : {e}"
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

        result = {

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


        print("=" * 60)

        print(
            "[RAG DIRECT] "
            f"Résultat : {result}"
        )

        print("=" * 60)


        return result


    # =========================================================
    # ANCIENNE MÉTHODE
    #
    # Conservée pour que main.py actuel continue de fonctionner
    # jusqu'à notre prochain commit.
    # =========================================================

    def ingest(
        self,
        limit=100,
        offset=0
    ):

        print(
            "[RAG INGESTION] "
            "Mode stockage local temporaire."
        )


        documents = (
            self.document_store._load()
        )


        return self.ingest_documents(

            documents=documents,

            limit=limit,

            offset=offset

        )


# =============================================================
# TEST RAG INGESTION
# =============================================================

def test_rag_ingestion():

    try:

        ingestion = (
            RAGIngestion()
        )


        return ingestion.ingest(

            limit=3,

            offset=0

        )


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
