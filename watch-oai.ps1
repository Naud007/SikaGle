param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [int]$RagLimit = 10,

    [int]$CheckIntervalSeconds = 30
)

$ErrorActionPreference = "Continue"

$BASE_URL = "https://sikagle-backend.onrender.com"

function Get-OaiStatus {

    try {
        $response = Invoke-WebRequest `
            "$BASE_URL/knowledge/oai-ingestion-status?source=$Source" `
            -TimeoutSec 30

        return ($response.Content | ConvertFrom-Json)
    }
    catch {
        Write-Host ""
        Write-Host "[OAI WATCH] Erreur de connexion :" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

function Start-OaiBatch {

    try {
        Write-Host ""
        Write-Host "[OAI AUTO] Lancement d'un batch de $RagLimit documents pour '$Source'..." -ForegroundColor Cyan

        $url = "$BASE_URL/knowledge/oai-ingestion-batch?source=$Source&rag_limit=$RagLimit"

        $response = Invoke-WebRequest `
            $url `
            -TimeoutSec 120

        return ($response.Content | ConvertFrom-Json)
    }
    catch {
        Write-Host ""
        Write-Host "[OAI AUTO] Erreur lors du lancement :" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " SikaGle - OAI-PMH WATCHER"
Write-Host "============================================================"
Write-Host ""
Write-Host "URL : $BASE_URL"
Write-Host "Source : $Source"
Write-Host "Batch : $RagLimit documents"
Write-Host "Intervalle : $CheckIntervalSeconds secondes"
Write-Host ""
Write-Host "Watcher demarre. CTRL+C pour arreter."
Write-Host ""

while ($true) {

    $statusBefore = Get-OaiStatus

    if ($null -eq $statusBefore) {
        Write-Host ""
        Write-Host "[OAI WATCH] Impossible de recuperer l'etat." -ForegroundColor Yellow
        Write-Host "Prochaine verification dans $CheckIntervalSeconds secondes..."
        Start-Sleep -Seconds $CheckIntervalSeconds
        continue
    }

    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Etat OAI ($Source)"

    Write-Host "  Documents traites : $($statusBefore.documents_processed)"
    Write-Host "  Total documents   : $($statusBefore.total_documents)"
    Write-Host "  Offset            : $($statusBefore.document_offset)"
    Write-Host "  Statut             : $($statusBefore.pipeline_status)"

    if ($statusBefore.pipeline_status -eq "completed") {

        Write-Host ""
        Write-Host "============================================================"
        Write-Host " $Source TERMINE"
        Write-Host "============================================================"
        Write-Host ""
        Write-Host "Tous les documents disponibles ont ete traites." -ForegroundColor Green
        Write-Host ""

        break
    }

    $oldOffset = $statusBefore.document_offset

    $batchResult = Start-OaiBatch

    if ($null -eq $batchResult) {
        Write-Host ""
        Write-Host "[OAI AUTO] Batch non lance ou timeout." -ForegroundColor Yellow
        Write-Host "Le prochain cycle reessaiera automatiquement."
        Write-Host ""

        Start-Sleep -Seconds $CheckIntervalSeconds
        continue
    }

    # =========================================================
    # CORRECTIF (leçon apprise avec watch-fao.ps1) :
    #
    # watch-fao.ps1 affichait "Batch termine" meme quand la
    # reponse serveur etait en realite {"status":"error",...},
    # car il ne verifiait jamais ce champ. Ici, on verifie
    # explicitement $batchResult.status avant d'afficher quoi
    # que ce soit comme un succes.
    # =========================================================

    if ($batchResult.status -eq "error") {

        Write-Host ""
        Write-Host "[OAI AUTO] ERREUR retournee par le serveur :" -ForegroundColor Red
        Write-Host "  $($batchResult.message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Le prochain cycle reessaiera automatiquement."

        Start-Sleep -Seconds $CheckIntervalSeconds
        continue
    }

    if ($batchResult.status -eq "completed") {

        Write-Host ""
        Write-Host "============================================================"
        Write-Host " $Source TERMINE"
        Write-Host "============================================================"
        Write-Host ""
        Write-Host "Tous les documents disponibles ont ete traites." -ForegroundColor Green
        Write-Host ""

        break
    }

    Write-Host ""
    Write-Host "[OAI AUTO] Batch termine." -ForegroundColor Green

    Write-Host "  Documents traites (batch) : $($batchResult.batch_processed)"
    Write-Host "  Inseres                    : $($batchResult.inserted)"
    Write-Host "  Mis a jour                 : $($batchResult.updated)"
    Write-Host "  Filtres                    : $($batchResult.filtered_out)"
    Write-Host "  Ignores (sans contenu)     : $($batchResult.skipped)"
    Write-Host "  Erreurs                    : $($batchResult.errors)"
    Write-Host "  Nouvel offset              : $($batchResult.next_document_offset)"

    $newOffset = $batchResult.next_document_offset

    if ($newOffset -eq $oldOffset) {

        Write-Host ""
        Write-Host "[OAI AUTO] ATTENTION : aucune progression detectee." -ForegroundColor Yellow

    }
    else {

        Write-Host ""
        Write-Host "[OAI AUTO] Progression : $oldOffset -> $newOffset" -ForegroundColor Green

    }

    Write-Host ""
    Write-Host "Prochaine verification dans $CheckIntervalSeconds secondes..."
    Write-Host ""

    Start-Sleep -Seconds $CheckIntervalSeconds
}