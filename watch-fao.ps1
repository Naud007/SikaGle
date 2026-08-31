$ErrorActionPreference = "Continue"

$BASE_URL = "https://sikagle-backend.onrender.com"

$RAG_LIMIT = 16
$MAX_BATCHES = 1
$CHECK_INTERVAL_SECONDS = 30

function Get-FaoStatus {

    try {
        $response = Invoke-WebRequest `
            "$BASE_URL/knowledge/fao-dataset-status" `
            -TimeoutSec 30

        return ($response.Content | ConvertFrom-Json)
    }
    catch {
        Write-Host ""
        Write-Host "[FAO WATCH] Erreur de connexion :" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

function Start-FaoBatch {

    try {
        Write-Host ""
        Write-Host "[FAO AUTO] Lancement d'un batch de $RAG_LIMIT documents..." -ForegroundColor Cyan

        $url = "$BASE_URL/knowledge/fao-dataset-pipeline-auto?rag_limit=$RAG_LIMIT&max_batches=$MAX_BATCHES"

        $response = Invoke-WebRequest `
            $url `
            -TimeoutSec 120

        return ($response.Content | ConvertFrom-Json)
    }
    catch {
        Write-Host ""
        Write-Host "[FAO AUTO] Erreur lors du lancement :" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " SikaGle - FAO AGRIS WATCHER"
Write-Host "============================================================"
Write-Host ""
Write-Host "URL : $BASE_URL"
Write-Host "Batch : $RAG_LIMIT documents"
Write-Host "Intervalle : $CHECK_INTERVAL_SECONDS secondes"
Write-Host ""
Write-Host "Watcher demarre. CTRL+C pour arreter."
Write-Host ""

while ($true) {

    $statusBefore = Get-FaoStatus

    if ($null -eq $statusBefore) {
        Write-Host ""
        Write-Host "[FAO WATCH] Impossible de recuperer l'etat." -ForegroundColor Yellow
        Write-Host "Prochaine verification dans $CHECK_INTERVAL_SECONDS secondes..."
        Start-Sleep -Seconds $CHECK_INTERVAL_SECONDS
        continue
    }

    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Etat FAO"

    Write-Host "  Datasets termines : $($statusBefore.datasets_completed)"
    Write-Host "  Dataset actuel    : $($statusBefore.dataset_offset)"
    Write-Host "  Document offset   : $($statusBefore.document_offset)"
    Write-Host "  Documents traites : $($statusBefore.documents_processed)"
    Write-Host "  Statut             : $($statusBefore.pipeline_status)"

    $oldOffset = $statusBefore.document_offset

    $batchResult = Start-FaoBatch

    if ($null -eq $batchResult) {
        Write-Host ""
        Write-Host "[FAO AUTO] Batch non lance ou timeout." -ForegroundColor Yellow
        Write-Host "Le prochain cycle reessaiera automatiquement."
        Write-Host ""

        Start-Sleep -Seconds $CHECK_INTERVAL_SECONDS
        continue
    }

    Write-Host ""
    Write-Host "[FAO AUTO] Batch termine." -ForegroundColor Green

    if ($null -ne $batchResult.result) {

        $result = $batchResult.result

        Write-Host "  Documents traites : $($result.documents_processed)"
        Write-Host "  Inseres            : $($result.inserted)"
        Write-Host "  Mis a jour         : $($result.updated)"
        Write-Host "  Filtres            : $($result.skipped)"
        Write-Host "  Erreurs            : $($result.errors)"
        Write-Host "  Nouvel offset      : $($result.next_document_offset)"
        Write-Host "  Datasets termines  : $($result.datasets_completed)"
        Write-Host "  Statut             : $($result.pipeline_status)"

        $newOffset = $result.next_document_offset

        if ($newOffset -eq $oldOffset) {

            Write-Host ""
            Write-Host "[FAO AUTO] ATTENTION : aucune progression detectee." -ForegroundColor Yellow

        }
        else {

            Write-Host ""
            Write-Host "[FAO AUTO] Progression : $oldOffset -> $newOffset" -ForegroundColor Green

        }

        if ($result.has_more_datasets -eq $false) {

            Write-Host ""
            Write-Host "============================================================"
            Write-Host " FAO AGRIS TERMINE"
            Write-Host "============================================================"
            Write-Host ""
            Write-Host "Tous les datasets disponibles ont ete traites." -ForegroundColor Green
            Write-Host ""

            break
        }
    }

    Write-Host ""
    Write-Host "Prochaine verification dans $CHECK_INTERVAL_SECONDS secondes..."
    Write-Host ""

    Start-Sleep -Seconds $CHECK_INTERVAL_SECONDS
}