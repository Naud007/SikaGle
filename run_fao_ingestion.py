import argparse
import os
import sys
import time

sys.path.insert(
    0,
    os.path.dirname(
        os.path.abspath(__file__)
    ),
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Ingestion FAO AGRIS en local "
            "(pas via Render)."
        )
    )

    parser.add_argument(
        "--jina-key",
        required=True,
        help=(
            "Clé API Jina à utiliser pour "
            "cette session d'ingestion."
        ),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help=(
            "Nombre de documents traités "
            "par batch (défaut : 100)."
        ),
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3,
        help=(
            "Pause en secondes entre deux "
            "batches (défaut : 3)."
        ),
    )

    args = parser.parse_args()

    # =====================================================
    # IMPORTANT : la clé Jina doit être définie AVANT
    # d'importer quoi que ce soit du projet, car
    # app.core.settings la lit une seule fois au chargement.
    # =====================================================

    os.environ["JINA_API_KEY"] = (
        args.jina_key
    )

    from dotenv import load_dotenv

    load_dotenv()

    from app.knowledge_engine.ingestion.fao_ingestion_worker import (
        FAOIngestionWorker,
    )

    worker = FAOIngestionWorker()

    print("=" * 60)
    print(" SikaGlé - FAO INGESTION (LOCAL)")
    print("=" * 60)
    print()
    print(f"Taille de batch : {args.batch_size}")
    print(f"Intervalle : {args.interval}s")
    print()
    print(
        "Démarrage. CTRL+C pour arrêter "
        "(la progression est sauvegardée "
        "après chaque batch)."
    )
    print()

    while True:

        try:

            result = worker.run_batch(
                dataset_limit=1,
                rag_limit=args.batch_size,
            )

        except Exception as e:

            print()
            print(
                "❌ Erreur pendant le batch : "
                f"{e}"
            )
            print(
                "Nouvel essai dans "
                f"{args.interval}s..."
            )

            time.sleep(args.interval)

            continue

        if result.get("status") == "completed":

            print()
            print("=" * 60)
            print(" FAO AGRIS TERMINÉ")
            print("=" * 60)
            print()
            print(
                "Tous les datasets disponibles "
                "ont été traités."
            )

            break

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"Datasets terminés : "
            f"{result.get('datasets_completed')} | "
            f"Offset document : "
            f"{result.get('next_document_offset')} | "
            f"Documents traités : "
            f"{result.get('documents_processed')} | "
            f"Insérés : {result.get('inserted')} | "
            f"Erreurs : {result.get('errors')} | "
            f"Statut : {result.get('pipeline_status')}"
        )

        time.sleep(args.interval)


if __name__ == "__main__":

    main()