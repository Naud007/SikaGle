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
            "Ingestion OAI-PMH générique en local "
            "(AfricaRice, IRRI, Bioversity, CIFOR, "
            "ICRISAT, et toute future source)."
        )
    )

    parser.add_argument(
        "--source",
        required=True,
        help=(
            "Nom de la source (ex: icrisat, irri, "
            "bioversity, cifor, africarice)."
        ),
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

    from app.knowledge_engine.ingestion.oai_ingestion_worker import (
        OAIIngestionWorker,
    )

    worker = OAIIngestionWorker(
        args.source
    )

    print("=" * 60)
    print(f" SikaGlé - OAI INGESTION (LOCAL) - {args.source}")
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
                rag_limit=args.batch_size
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
            print(f" {args.source.upper()} TERMINÉ")
            print("=" * 60)
            print()
            print(
                "Tous les documents disponibles "
                "ont été traités."
            )

            break

        if result.get("status") == "error":

            print()
            print(
                "❌ ERREUR retournée : "
                f"{result.get('message')}"
            )
            print(
                "Nouvel essai dans "
                f"{args.interval}s..."
            )

            time.sleep(args.interval)

            continue

        print(
            f"[{time.strftime('%H:%M:%S')}] "
            f"Offset : {result.get('batch_offset')} -> "
            f"{result.get('next_document_offset')} / "
            f"{result.get('total_documents')} | "
            f"Insérés : {result.get('inserted')} | "
            f"Filtrés licence : {result.get('licensed_out')} | "
            f"Erreurs : {result.get('errors')}"
        )

        time.sleep(args.interval)


if __name__ == "__main__":

    main()