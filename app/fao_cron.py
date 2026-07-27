import sys
import requests


PIPELINE_URL = (
    "https://sikagle-backend.onrender.com/"
    "knowledge/fao-dataset-pipeline-test"
)


def run():

    print("=" * 60)
    print("[FAO CRON] Démarrage de l'ingestion AGRIS")
    print("=" * 60)

    try:

        response = requests.get(
            PIPELINE_URL,
            params={
                "dataset_limit": 1,
                "rag_limit": 3,
            },
            timeout=240,
        )

        response.raise_for_status()

        result = response.json()

        print(
            "[FAO CRON] Réponse du pipeline :"
        )

        print(result)

        if result.get("status") == "error":

            print(
                "[FAO CRON] Le pipeline "
                "a retourné une erreur."
            )

            sys.exit(1)

        print(
            "[FAO CRON] Exécution terminée avec succès."
        )

    except Exception as e:

        print(
            f"[FAO CRON] Erreur : {e}"
        )

        sys.exit(1)


if __name__ == "__main__":

    run()
