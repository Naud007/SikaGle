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
# INGESTION DES DOCUMENTS DANS LE RAG
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


        # =====================================================
        # CONNEXION SUPABASE
        # =====================================================

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

            existing_sources = set()

            batch_size = 1000
            offset = 0


            while True:

                response = (

                    self.supabase

                    .table(
                        "documents_rag"
                    )

                    .select(
                        "source_path"
                    )

                    .range(
                        offset,
                        offset + batch_size - 1
                    )

                    .execute()

                )


                rows = (
                    response.data
                    or []
                )


                if not rows:

                    break


                for row in rows:

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


                if len(
                    rows
                ) < batch_size:

                    break


                offset += (
                    batch_size
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
    # EXTRAIRE L'URL / SOURCE UNIQUE
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


        return (
            "Document sans titre"
        )


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
    # EXTRAIRE LE NOM DE LA SOURCE / ORGANISME
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
    # EXTRAIRE LA LANGUE
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


        if not language:

            return None


        language = str(
            language
        ).strip()


        return (
            language
            if language
            else None
        )


    # =========================================================
    # EXTRAIRE LE TYPE DE DOCUMENT
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


        if not document_type:

            return None


        document_type = str(
            document_type
        ).strip()


        return (
            document_type
            if document_type
            else None
        )


    # =========================================================
    # EXTRAIRE LA CULTURE
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


        if not crop:

            return None


        crop = str(
            crop
        ).strip()


        return (
            crop
            if crop
            else None
        )


    # =========================================================
    # EXTRAIRE LA ZONE GÉOGRAPHIQUE
    # =========================================================

    def get_document_geographic_area(
        self,
        document
    ):

        # -----------------------------------------------------
        # PRIORITÉ À LA ZONE GÉOGRAPHIQUE EXPLICITE
        # -----------------------------------------------------

        zone = document.get(
            "zone_geographique"
        )


        if zone:

            zone = str(
                zone
            ).strip()

            if zone:

                return zone


        # -----------------------------------------------------
        # SINON UTILISER LE PAYS S'IL EST RÉELLEMENT CONNU
        # -----------------------------------------------------

        country = document.get(
            "country"
        )


        if country:

            country = str(
                country
            ).strip()

            if country:

                return country


        # -----------------------------------------------------
        # IMPORTANT :
        # AUCUN "BÉNIN" AUTOMATIQUE
        # -----------------------------------------------------

        return None


    # =========================================================
    # EXTRAIRE LES MOTS-CLÉS
    # =========================================================

    def get_document_keywords(
        self,
        document
    ):

        keywords = (
            document.get(
                "keywords"
            )
            or
            document.get(
                "mots_cles"
            )
        )


        if not keywords:

            return None


        # -----------------------------------------------------
        # LISTE DE MOTS-CLÉS
        # -----------------------------------------------------

        if isinstance(
            keywords,
            list
        ):

            cleaned = []

            for keyword in keywords:

                if keyword is None:

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


        # -----------------------------------------------------
        # CHAÎNE DE CARACTÈRES
        # -----------------------------------------------------

        value = str(
            keywords
        ).strip()


        if not value:

            return None


        return [
            value
        ]


    # =========================================================
    # EXTRAIRE L'ANNÉE
    # =========================================================

    def get_document_year(
        self,
        document
    ):

        # -----------------------------------------------------
        # FORMAT DÉJÀ PRÉSENT
        # -----------------------------------------------------

        year = (
            document.get(
                "year"
            )
            or
            document.get(
                "annee"
            )
        )


        if year:

            value = str(
                year
            ).strip()


            if len(
                value
            ) >= 4:

                try:

                    parsed_year = int(
                        value[:4]
                    )


                    if (
                        1000
                        <= parsed_year
                        <= 9999
                    ):

                        return parsed_year


                except Exception:

                    pass


        # -----------------------------------------------------
        # FORMAT published_at
        # -----------------------------------------------------

        published_at = document.get(
            "published_at"
        )


        if published_at:

            value = str(
                published_at
            ).strip()


            if len(
                value
            ) >= 4:

                try:

                    parsed_year = int(
                        value[:4]
                    )


                    if (
                        1000
                        <= parsed_year
                        <= 9999
                    ):

                        return parsed_year


                except Exception:

                    pass


        return None


    # =========================================================
    # CONSTRUIRE LE TEXTE POUR LE RAG
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


        document_type = (
            self.get_document_type(
                document
            )
        )


        crop = (
            self.get_document_crop(
                document
            )
        )


        geographic_area = (
            self.get_document_geographic_area(
                document
            )
        )


        keywords = (
            self.get_document_keywords(
                document
            )
        )


        year = (
            self.get_document_year(
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
        # ANNÉE
        # -----------------------------------------------------

        if year:

            parts.append(
                f"Année : {year}"
            )


        # -----------------------------------------------------
        # LANGUE
        # -----------------------------------------------------

        if language:

            parts.append(
                f"Langue : {language}"
            )


        # -----------------------------------------------------
        # TYPE
        # -----------------------------------------------------

        if document_type:

            parts.append(
                "Type de document : "
                f"{document_type}"
            )


        # -----------------------------------------------------
        # CULTURE
        # -----------------------------------------------------

        if crop:

            parts.append(
                f"Culture : {crop}"
            )


        # -----------------------------------------------------
        # LOCALISATION
        # -----------------------------------------------------

        if geographic_area:

            parts.append(
                "Zone géographique : "
                f"{geographic_area}"
            )


        # -----------------------------------------------------
        # MOTS-CLÉS
        # -----------------------------------------------------

        if keywords:

            parts.append(
                "Mots-clés : "
                + ", ".join(
                    keywords
                )
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
                "limit doit être supérieur à 0."
            )


        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )


        # =====================================================
        # CHARGER LES DOCUMENTS LOCAUX
        # =====================================================

        print(
            "[RAG INGESTION] "
            "Chargement des documents "
            "depuis le stockage local..."
        )


        all_documents = (
            self.document_store._load()
        )


        total_documents = len(
            all_documents
        )


        print(
            "[RAG INGESTION] "
            f"{total_documents} document(s) "
            "disponible(s)."
        )


        # =====================================================
        # AUCUN DOCUMENT
        # =====================================================

        if total_documents == 0:

            return {

                "status":
                    "success",

                "message":
                    "Aucun document disponible.",

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
        # SOURCES DÉJÀ INGÉRÉES
        # =====================================================

        existing_sources = (
            self.get_existing_sources()
        )


        # =====================================================
        # SÉLECTIONNER LE BATCH
        # =====================================================

        batch = all_documents[
            offset:
            offset + limit
        ]


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
        # TRAITER LES DOCUMENTS
        # =====================================================

        for index, document in enumerate(
            batch,
            start=offset + 1
        ):

            try:

                # -------------------------------------------------
                # FORMAT
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


                language = (
                    self.get_document_language(
                        document
                    )
                )


                document_type = (
                    self.get_document_type(
                        document
                    )
                )


                crop = (
                    self.get_document_crop(
                        document
                    )
                )


                geographic_area = (
                    self.get_document_geographic_area(
                        document
                    )
                )


                keywords = (
                    self.get_document_keywords(
                        document
                    )
                )


                year = (
                    self.get_document_year(
                        document
                    )
                )


                # -------------------------------------------------
                # CONTENU OBLIGATOIRE
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
                # DOUBLONS
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
                # TEXTE RAG
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
                # EMBEDDING
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
                        language,

                    "type_document":
                        document_type,

                    "culture":
                        crop,

                    "zone_geographique":
                        geographic_area,

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
                # RETIRER LES VALEURS None
                #
                # Cela évite d'inventer des métadonnées.
                # -------------------------------------------------

                row = {

                    key: value

                    for key, value
                    in row.items()

                    if value is not None

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
                        url
                    )


                print(
                    f"✅ [{index}] "
                    "Document inséré : "
                    f"{title[:80]}"
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
                    f"❌ [{index}] "
                    "Erreur ingestion : "
                    f"{e}"
                )


        # =====================================================
        # RÉSULTAT
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
            limit=10,
            offset=0
        )


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
