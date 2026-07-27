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
    # CHARGER LES DOCUMENTS DÉJÀ PRÉSENTS
    # =========================================================

    def get_existing_documents(self):

        print(
            "[RAG INGESTION] "
            "Chargement des documents existants..."
        )

        existing_documents = {}

        batch_size = 1000
        offset = 0

        try:

            while True:

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

                    .range(
                        offset,
                        offset + batch_size - 1
                    )

                    .execute()
                )

                batch = (
                    response.data
                    or []
                )

                if not batch:
                    break

                for row in batch:

                    source_path = (
                        row.get(
                            "source_path"
                        )
                    )

                    if source_path:

                        source_path = str(
                            source_path
                        ).strip()

                        existing_documents[
                            source_path
                        ] = row

                if len(batch) < batch_size:
                    break

                offset += batch_size

            print(
                "[RAG INGESTION] "
                f"{len(existing_documents)} "
                "source(s) existante(s)."
            )

            return existing_documents

        except Exception as e:

            print(
                "[RAG INGESTION] "
                "Erreur chargement documents :",
                e
            )

            return {}


    # =========================================================
    # SOURCE UNIQUE DU DOCUMENT
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
            document.get(
                "title"
            )
            or
            document.get(
                "titre"
            )
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
    # ORGANISME / SOURCE
    # =========================================================

    def get_document_source_name(
        self,
        document
    ):

        source = (
            document.get(
                "source"
            )
            or
            document.get(
                "organisme"
            )
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
            document.get(
                "language"
            )
            or
            document.get(
                "langue"
            )
        )

        if language:

            language = str(
                language
            ).strip().lower()

            # ---------------------------------------------
            # NORMALISATION
            # ---------------------------------------------

            language_map = {

                "english":
                    "en",

                "eng":
                    "en",

                "en":
                    "en",

                "french":
                    "fr",

                "fra":
                    "fr",

                "fre":
                    "fr",

                "fr":
                    "fr",

                "français":
                    "fr",

                "portuguese":
                    "pt",

                "por":
                    "pt",

                "pt":
                    "pt",

                "spanish":
                    "es",

                "spa":
                    "es",

                "es":
                    "es",

            }

            if language in language_map:

                return language_map[
                    language
                ]

            return language

        # ---------------------------------------------
        # FALLBACK
        #
        # Les datasets AGRIS actuellement traités
        # sont majoritairement en anglais.
        # ---------------------------------------------

        return "en"


    # =========================================================
    # CULTURE
    # =========================================================

    def get_document_crop(
        self,
        document
    ):

        crop = (
            document.get(
                "crop"
            )
            or
            document.get(
                "culture"
            )
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

                if keyword:

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

            values = [

                value.strip()

                for value
                in keywords.split(",")

                if value.strip()

            ]

            return (
                values
                if values
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
    # VÉRIFIER SI LE CONTENU RAG A CHANGÉ
    # =========================================================

    def content_has_changed(
        self,
        existing_document,
        new_content
    ):

        existing_content = (
            existing_document.get(
                "content"
            )
            or ""
        )

        return (
            existing_content.strip()
            != new_content.strip()
        )


    # =========================================================
    # INGESTION
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
                "limit doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )


        # =====================================================
        # CHARGER DOCUMENTS LOCAUX
        # =====================================================

        print(
            "[RAG INGESTION] "
            "Chargement des documents locaux..."
        )

        all_documents = (
            self.document_store._load()
        )

        total_documents = len(
            all_documents
        )

        print(
            "[RAG INGESTION] "
            f"{total_documents} document(s) disponible(s)."
        )


        # =====================================================
        # AUCUN DOCUMENT
        # =====================================================

        if total_documents == 0:

            return {

                "status":
                    "success",

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
        # DOCUMENTS EXISTANTS SUPABASE
        # =====================================================

        existing_documents = (
            self.get_existing_documents()
        )


        # =====================================================
        # BATCH
        # =====================================================

        batch = (

            all_documents[

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

        for index, document in enumerate(
            batch,
            start=offset + 1
        ):

            try:

                # =================================================
                # FORMAT
                # =================================================

                if not isinstance(
                    document,
                    dict
                ):

                    errors += 1

                    continue


                # =================================================
                # DONNÉES
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
                # URL OBLIGATOIRE POUR DÉDOUBLONNAGE
                # =================================================

                if not url:

                    print(
                        f"⚠️ [{index}] "
                        f"Document sans URL : {title}"
                    )

                    errors += 1

                    continue


                # =================================================
                # CONTENU RAG
                # =================================================

                rag_text = (
                    self.build_rag_text(
                        document
                    )
                )


                if not rag_text.strip():

                    print(
                        f"⚠️ [{index}] "
                        f"Contenu vide : {title}"
                    )

                    errors += 1

                    continue


                # =================================================
                # LIGNE DE BASE
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

                existing = (
                    existing_documents.get(
                        url
                    )
                )


                if existing:

                    document_id = (
                        existing.get(
                            "id"
                        )
                    )


                    # =============================================
                    # CONTENU MODIFIÉ ?
                    # =============================================

                    content_changed = (
                        self.content_has_changed(
                            existing,
                            rag_text
                        )
                    )


                    # =============================================
                    # SI CONTENU MODIFIÉ :
                    # REFAIRE EMBEDDING
                    # =============================================

                    if content_changed:

                        print(
                            f"🔄 [{index}] "
                            f"Mise à jour + embedding : "
                            f"{title[:80]}"
                        )

                        embedding = (

                            self.embedding_service

                            .generate_document_embedding(
                                rag_text
                            )

                        )

                        if not embedding:

                            print(
                                f"❌ [{index}] "
                                "Embedding vide."
                            )

                            errors += 1

                            continue

                        row[
                            "embedding"
                        ] = embedding

                        time.sleep(
                            0.7
                        )

                    else:

                        print(
                            f"📝 [{index}] "
                            f"Mise à jour métadonnées : "
                            f"{title[:80]}"
                        )


                    # =============================================
                    # UPDATE SUPABASE
                    # =============================================

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


                    existing_documents[
                        url
                    ] = {

                        **existing,

                        **row

                    }


                    print(
                        f"✅ [{index}] "
                        f"Document mis à jour."
                    )

                    continue


                # =================================================
                # NOUVEAU DOCUMENT
                # =================================================

                print(
                    f"🤖 [{index}] "
                    f"Nouvel embedding : "
                    f"{title[:80]}"
                )


                embedding = (

                    self.embedding_service

                    .generate_document_embedding(
                        rag_text
                    )

                )


                if not embedding:

                    print(
                        f"❌ [{index}] "
                        "Embedding vide."
                    )

                    errors += 1

                    continue


                row[
                    "embedding"
                ] = embedding


                # =================================================
                # INSERT SUPABASE
                # =================================================

                response = (

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


                # =================================================
                # AJOUT AU CACHE
                # =================================================

                inserted_row = None

                if response.data:

                    inserted_row = (
                        response.data[0]
                    )


                existing_documents[
                    url
                ] = (
                    inserted_row
                    or row
                )


                print(
                    f"✅ [{index}] "
                    f"Nouveau document inséré."
                )


                time.sleep(
                    0.7
                )


            except Exception as e:

                errors += 1

                print(
                    f"❌ [{index}] "
                    f"Erreur ingestion : {e}"
                )


        # =====================================================
        # PROCHAIN OFFSET
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
