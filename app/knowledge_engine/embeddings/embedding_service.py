from fastembed import TextEmbedding

from app.core import settings


class LocalEmbeddingService:
    """
    Service local de génération d'embeddings.

    Utilise FastEmbed + ONNX Runtime.
    Modèle multilingue :
    intfloat/multilingual-e5-small

    Dimension :
    384
    """

    def __init__(
        self,
        model=None,
    ):

        self.model_name = (
            model
            or settings.EMBEDDING_MODEL
        )

        self.output_dimensionality = (
            settings.EMBEDDING_DIMENSION
        )

        self.client = TextEmbedding(
            model_name=self.model_name
        )

    # =========================================================
    # EMBEDDING DOCUMENT UNIQUE
    # =========================================================

    def generate_document_embedding(
        self,
        text: str,
    ):

        if not text or not text.strip():

            raise ValueError(
                "Le texte à encoder est vide."
            )

        embeddings = list(
            self.client.passage_embed(
                [text.strip()]
            )
        )

        if not embeddings:

            raise ValueError(
                "Aucun embedding document généré."
            )

        vector = embeddings[0]

        values = vector.tolist()

        if len(values) != (
            self.output_dimensionality
        ):

            raise ValueError(
                "Dimension d'embedding inattendue : "
                f"{len(values)} au lieu de "
                f"{self.output_dimensionality}."
            )

        return values

    # =========================================================
    # EMBEDDINGS DOCUMENTS
    # =========================================================

    def generate_document_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Génère les embeddings de plusieurs documents
        localement.

        Aucun appel Gemini n'est effectué.
        """

        if not texts:

            raise ValueError(
                "La liste des textes à encoder "
                "est vide."
            )

        cleaned_texts = []

        for text in texts:

            if not text or not text.strip():

                raise ValueError(
                    "Un des textes à encoder "
                    "est vide."
                )

            cleaned_texts.append(
                text.strip()
            )

        embeddings = list(
            self.client.passage_embed(
                cleaned_texts
            )
        )

        if len(embeddings) != len(
            cleaned_texts
        ):

            raise ValueError(
                "Le nombre d'embeddings générés "
                "ne correspond pas au nombre "
                "de textes."
            )

        result = []

        for embedding in embeddings:

            values = embedding.tolist()

            if len(values) != (
                self.output_dimensionality
            ):

                raise ValueError(
                    "Dimension d'embedding "
                    "inattendue : "
                    f"{len(values)} au lieu de "
                    f"{self.output_dimensionality}."
                )

            result.append(values)

        return result

    # =========================================================
    # EMBEDDING REQUÊTE
    # =========================================================

    def generate_query_embedding(
        self,
        text: str,
    ):

        if not text or not text.strip():

            raise ValueError(
                "La requête à encoder est vide."
            )

        embeddings = list(
            self.client.query_embed(
                [text.strip()]
            )
        )

        if not embeddings:

            raise ValueError(
                "Aucun embedding de requête "
                "généré."
            )

        vector = embeddings[0]

        values = vector.tolist()

        if len(values) != (
            self.output_dimensionality
        ):

            raise ValueError(
                "Dimension d'embedding "
                "inattendue : "
                f"{len(values)} au lieu de "
                f"{self.output_dimensionality}."
            )

        return values


# =========================================================
# TEST EMBEDDING
# =========================================================

def test_embedding():

    try:

        embedding_service = (
            LocalEmbeddingService()
        )

        vector = (
            embedding_service
            .generate_document_embedding(
                "Comment cultiver "
                "le maïs au Bénin ?"
            )
        )

        return {

            "status": "success",

            "model":
                embedding_service.model_name,

            "dimension":
                len(vector),

            "expected_dimension":
                embedding_service
                .output_dimensionality,

            "preview":
                vector[:5],
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e),
        }


# =========================================================
# COMPATIBILITÉ AVEC LE RESTE DU PROJET
# =========================================================

GeminiEmbeddingService = (
    LocalEmbeddingService
)

GeminiEmbedding = (
    LocalEmbeddingService
)