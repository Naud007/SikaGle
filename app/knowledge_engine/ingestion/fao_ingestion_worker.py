import os

from supabase import create_client, Client


class FAOIngestionWorker:

    PIPELINE_NAME = "fao_agris"

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
        # CLIENT SUPABASE
        # =====================================================

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key
            )
        )

    # =========================================================
    # LIRE L'ÉTAT DE PROGRESSION
    # =========================================================

    def get_state(self):

        response = (
            self.supabase
            .table(
                "fao_ingestion_state"
            )
            .select(
                "*"
            )
            .eq(
                "pipeline_name",
                self.PIPELINE_NAME
            )
            .limit(
                1
            )
            .execute()
        )

        rows = (
            response.data
            or []
        )

        if not rows:

            raise RuntimeError(
                "État d'ingestion FAO "
                "introuvable dans Supabase."
            )

        return rows[0]
