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

from dotenv import load_dotenv

load_dotenv()

from app.knowledge_engine.ingestion.plantvillage_ingestion_worker import (
    PlantVillageIngestionWorker,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Ingestion PlantVillage → Supabase "
            "(embeddings d'images via Jina)."
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
        default=50,
        help=(
            "Nombre d'images traitées par batch "
            "(défaut : 50)."
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

    worker = PlantVillageIngestionWorker(
        jina_api_key=args.jina_key
    )

    print("=" * 60)
    print(" SikaGlé - PLANTVILLAGE INGESTION")
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
                batch_size=args.batch_size
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

        if result["status"] == "completed":

            print()
            print("=" * 60)
            print(" PLANTVILLAGE TERMINÉ")
            print("=" * 60)
            print()
            print(
                "Toutes les images ont été "
                "traitées."
            )

            break

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"Batch : {result['batch_offset']} → "
            f"{result['next_image_offset']} / "
            f"{result['total_images']} "
            f"(insérées : {result['inserted']}, "
            f"erreurs : {result['errors']})"
        )

        time.sleep(args.interval)


if __name__ == "__main__":

    main()