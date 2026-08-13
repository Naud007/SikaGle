$BASE_URL = "https://sikagle-backend.onrender.com"

$RAG_LIMIT = 20

$WAIT_SECONDS = 30

Write-Host ""
Write-Host "=================================================="
Write-Host " SikaGlé - Pipeline FAO automatique"
Write-Host "=================================================="
Write-Host ""
Write-Host "Batch automatique : $RAG_LIMIT documents"
Write-Host "Vérification toutes les $WAIT_SECONDS secondes"
Write-Host ""
Write-Host "CTRL+C pour arrêter."
Write-Host ""

$lastOffset = -1

while ($true) {

    try {

        # ==================================================
        # 1. LIRE L'ETAT ACTUEL
        # ==================================================

        $statusUrl = "$BASE_URL/knowledge/fao-dataset-status"

        $response = Invoke-WebRequest `
            $statusUrl `
            -TimeoutSec 30

        $state = $response.Content | ConvertFrom-Json

        $datasetOffset = [int]($state.dataset_offset)
        $documentOffset = [int]($state.document_offset)
        $documentsProcessed = [int]($state.documents_processed)
        $datasetsCompleted = [int]($state.datasets_completed)
        $pipelineStatus = $state.pipeline_status
        $lastError = $state.last_error

        Write-Host ""
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Etat FAO"
        Write-Host "  Datasets terminés : $datasetsCompleted"
        Write-Host "  Dataset actuel    : $datasetOffset"
        Write-Host "  Document offset   : $documentOffset"
        Write-Host "  Documents traités : $documentsProcessed"
        Write-Host "  Statut            : $pipelineStatus"

        # ==================================================
        # 2. ERREUR
        # ==================================================

        if ($pipelineStatus -eq "error") {

            Write-Host ""
            Write-Host "ERREUR DU PIPELINE :" -ForegroundColor Red
            Write-Host $lastError -ForegroundColor Red

            break
        }

        # ==================================================
        # 3. FIN
        # ==================================================

        if ($pipelineStatus -eq "completed") {

            Write-Host ""
            Write-Host "=================================================="
            Write-Host " FAO TERMINÉ"
            Write-Host "=================================================="

            break
        }

        # ==================================================
        # 4. PIPELINE IDLE = LANCER UN BATCH
        # ==================================================

        if ($pipelineStatus -eq "idle") {

            Write-Host ""
            Write-Host "[FAO AUTO] Lancement d'un batch de $RAG_LIMIT documents..." `
                -ForegroundColor Cyan

            $pipelineUrl = "$BASE_URL/knowledge/fao-dataset-pipeline-auto?rag_limit=$RAG_LIMIT&max_batches=1"

            try {

                $launch = Invoke-WebRequest `
                    $pipelineUrl `
                    -TimeoutSec 30

                $launchData = (
                    $launch.Content |
                    ConvertFrom-Json
                )

                Write-Host ""
                Write-Host "[FAO AUTO] $($launchData.message)" `
                    -ForegroundColor Green

            }
            catch {

                Write-Host ""
                Write-Host "[FAO AUTO] Erreur lors du lancement :" `
                    -ForegroundColor Red

                Write-Host $_.Exception.Message `
                    -ForegroundColor Red
            }

            # ==================================================
            # 5. ATTENDRE LE TRAITEMENT
            # ==================================================

            Write-Host ""
            Write-Host "Attente de la fin du batch..."

            Start-Sleep -Seconds $WAIT_SECONDS

            # ==================================================
            # 6. VERIFIER LA PROGRESSION
            # ==================================================

            try {

                $check = Invoke-WebRequest `
                    $statusUrl `
                    -TimeoutSec 30

                $newState = (
                    $check.Content |
                    ConvertFrom-Json
                )

                $newOffset = [int](
                    $newState.document_offset
                )

                $newDocumentsProcessed = [int](
                    $newState.documents_processed
                )

                $newStatus = $newState.pipeline_status

                Write-Host ""
                Write-Host "[FAO AUTO] Vérification après batch"
                Write-Host "  Ancien offset : $documentOffset"
                Write-Host "  Nouvel offset : $newOffset"
                Write-Host "  Documents     : $newDocumentsProcessed"
                Write-Host "  Statut        : $newStatus"

                # ==================================================
                # 7. VERIFIER QUE LE BATCH A VRAIMENT AVANCE
                # ==================================================

                if ($newOffset -gt $documentOffset) {

                    Write-Host ""
                    Write-Host "[FAO AUTO] PROGRESSION CONFIRMÉE : +$($newOffset - $documentOffset) documents" `
                        -ForegroundColor Green
                }
                else {

                    Write-Host ""
                    Write-Host "[FAO AUTO] ATTENTION : aucune progression détectée." `
                        -ForegroundColor Yellow

                    Write-Host "Le prochain cycle relancera automatiquement le batch." `
                        -ForegroundColor Yellow
                }

            }
            catch {

                Write-Host ""
                Write-Host "[FAO AUTO] Erreur pendant la vérification :" `
                    -ForegroundColor Yellow

                Write-Host $_.Exception.Message `
                    -ForegroundColor Yellow
            }

            continue
        }

        # ==================================================
        # 8. AUTRE STATUT
        # ==================================================

        Write-Host ""
        Write-Host "Pipeline actuellement : $pipelineStatus"
        Write-Host "Attente avant nouvelle vérification..."

    }
    catch {

        Write-Host ""
        Write-Host "[FAO WATCH] Erreur de connexion :" `
            -ForegroundColor Red

        Write-Host $_.Exception.Message `
            -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Prochaine vérification dans $WAIT_SECONDS secondes..."

    Start-Sleep -Seconds $WAIT_SECONDS
}