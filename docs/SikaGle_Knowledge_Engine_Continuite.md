# SikaGlé --- État du projet et document de reprise

## 1. Objet

Document de reprise officiel du projet SikaGlé pour une nouvelle
conversation.

Il décrit l'état réel du projet, les décisions d'architecture, ce qui
est terminé, ce qui reste à faire et l'ordre recommandé jusqu'à la V1
client final.

**Règle : ne pas recommencer les travaux déjà validés.**

------------------------------------------------------------------------

## 2. Vision du produit

SikaGlé est un assistant agricole intelligent destiné en priorité aux
agriculteurs d'Afrique de l'Ouest.

Vision V1 :

> Un agriculteur peut envoyer une question par texte, voix ou image.
> SikaGlé comprend le problème, consulte les connaissances agricoles
> disponibles, raisonne sur le contexte et répond dans une langue
> adaptée à l'utilisateur.

Langues prévues pour la V1 :

-   Français
-   Fon
-   Yoruba
-   Dendi

Canal prioritaire :

-   WhatsApp

Parcours cible :

``` text
Agriculteur
   ↓
WhatsApp
   ↓
Texte / voix / image
   ↓
Compréhension
   ↓
Conversation Engine
   ↓
Knowledge Engine / RAG
   ↓
Raisonnement
   ↓
Réponse
   ↓
Texte ou voix
   ↓
Agriculteur
```

------------------------------------------------------------------------

## 3. Architecture actuelle

``` text
SOURCE DOCUMENTAIRE
        ↓
CONNECTEUR / DOWNLOADER
        ↓
PARSER / NORMALISATION
        ↓
DocumentMetadata
        ↓
AgriculturalRelevanceFilter
        ↓
RAGIngestion
        ↓
Construction du texte RAG
        ↓
Jina Embeddings
        ↓
Supabase
        ↓
knowledge_embeddings
        ↓
HybridRetriever
        ↓
RAGService
        ↓
Réponse + sources
```

Principe essentiel : les nouvelles sources doivent alimenter le pipeline
commun. Ne pas créer un RAG différent pour chaque source.

------------------------------------------------------------------------

## 4. État global

  Élément                       État
  ----------------------------- ------------------------------
  Infrastructure backend        ✅
  Knowledge Engine              ✅
  Supabase vector store         ✅
  Jina Embeddings 1024D         ✅
  RAG                           ✅
  AgriculturalRelevanceFilter   ⚠️ à améliorer
  BRAB                          ✅ 152/152 parcourus
  FAO / AGRIS                   🔄 à terminer
  INRAB                         ⏸ BRAB actuellement exploité
  ITA                           ⏳ après V1
  AfricaRice                    ⏳ après V1
  Refactor main.py              ⏳
  Conversation Engine           🔄 à finaliser
  Voix                          ⏳
  Image / Vision                ⏳
  Français                      🔄
  Fon                           ⏳
  Yoruba                        ⏳
  Dendi                         ⏳
  WhatsApp                      🔄
  Tests bout en bout            ⏳

------------------------------------------------------------------------

## 5. Knowledge Engine --- terminé

Les composants suivants sont fonctionnels :

-   FastAPI
-   logging
-   health checks
-   readiness
-   monitoring de base
-   Supabase
-   stockage vectoriel
-   embeddings 1024D
-   ingestion
-   parsing
-   filtrage agricole
-   retrieval
-   RAG

Table vectorielle :

``` text
knowledge_embeddings
```

Embedding :

``` text
vector(1024)
```

Recherche :

``` text
public.match_knowledge_embeddings(...)
```

Endpoint principal :

``` text
POST /knowledge/ask
```

Un test RAG a été validé avec une question sur les effets du changement
climatique sur l'agriculture au Bénin.

Résultat observé :

``` text
success = true
chunks_used = 5
source = BRAB
```

------------------------------------------------------------------------

## 6. BRAB --- TERMINÉ

BRAB est actuellement la source INRAB exploitable retenue.

Collection entièrement parcourue :

``` text
0    → 20   ✅
20   → 40   ✅
40   → 60   ✅
60   → 80   ✅
80   → 100  ✅
100  → 120  ✅
120  → 140  ✅
140  → 152  ✅
```

Résultat :

``` text
152 / 152 documents parcourus
```

Dernier batch :

``` text
documents_found = 12
downloaded = 11
validated = 11
indexed = 7
skipped = 4
filtered_out = 1
failed = 0
errors = []
```

BRAB est donc terminé pour cette phase d'ingestion.

------------------------------------------------------------------------

## 7. Incident Jina --- CORRIGÉ

Pendant BRAB, Jina avait retourné :

``` text
HTTP 429
RATE_TOKEN_LIMIT_EXCEEDED
```

Exemple :

``` text
109,179 / 100,000 tokens per minute
```

Correction dans :

``` text
app/knowledge_engine/embeddings/embedding_service.py
```

Configuration actuelle :

``` text
MAX_BATCH_SIZE = 5
MAX_RETRIES = 5
INITIAL_DELAY_SECONDS = 2
REQUEST_DELAY_SECONDS = 2
```

Ajouts :

-   retry automatique ;
-   backoff progressif ;
-   délai entre requêtes ;
-   gestion spécifique du HTTP 429 ;
-   gestion des erreurs réseau ;
-   validation des embeddings.

Après correction, le batch BRAB `offset=140` a réussi :

``` text
failed = 0
errors = []
indexed = 7
```

------------------------------------------------------------------------

## 8. Double comptage des erreurs --- CORRIGÉ

Le fichier :

``` text
app/knowledge_engine/ingestion/ingestion_report.py
```

a été corrigé.

Avant, `add_error()` incrémentait `failed`, alors que l'orchestration
pouvait aussi incrémenter `failed`.

Désormais :

``` text
add_error()
```

enregistre uniquement l'erreur.

Le compteur `failed` est géré au niveau de l'orchestration du document.

------------------------------------------------------------------------

## 9. AgriculturalRelevanceFilter

Fichier :

``` text
app/knowledge_engine/filters/agricultural_relevance.py
```

Le filtre est intégré au pipeline RAG avant l'embedding.

Il sait déjà rejeter des contenus manifestement hors domaine agricole.

### Problème connu

Un faux positif a été identifié :

``` text
A systematic literature review on food and nutrition research
in Benin and how research integrate equity lens
for healthier food choices
```

Il a été rejeté à cause de :

``` text
literature
```

Autre cas à surveiller :

``` text
Overview of technological feed manufacturing processes
and criteria for the manufacture of an extruder
for fish feed in Benin: Literature review
```

Ce document est lié à l'alimentation animale / aquaculture et doit être
considéré comme pertinent.

Conclusion :

``` text
literature
systematic review
literature review
```

ne doivent pas, à eux seuls, provoquer l'exclusion.

### Travail restant

1.  revoir les règles d'exclusion ;
2.  supprimer les faux positifs ;
3.  ajouter des tests de régression ;
4.  tester agriculture, élevage, aquaculture, agroalimentaire, sols,
    climat agricole, etc. ;
5.  valider le filtre avant la suite.

**Ne pas modifier le filtre sans tests.**

------------------------------------------------------------------------

## 10. FAO / AGRIS --- EN COURS

Le pipeline AGRIS fonctionne.

Source :

``` text
https://agris.fao.org/ods/AGRIS.ODS.xml
```

Catalogue :

``` text
AGRIS.ODS.xml
```

Statistique observée :

``` text
datasets_found = 1235
```

Dataset testé :

``` text
AGRIS.ODS.BRI.xml
```

Résultat :

``` text
documents_parsed = 784
```

Test réel :

``` text
dataset_limit = 1
rag_limit = 5
```

Résultat :

``` text
datasets_processed = 1
datasets_success = 1
datasets_errors = 0
documents_parsed = 784
inserted = 2
updated = 0
skipped = 0
errors = 0
documents_processed = 739
datasets_completed = 1
next_dataset_offset = 1
next_document_offset = 725
has_more_datasets = true
pipeline_status = idle
```

Batch RAG :

``` text
total_documents = 784
batch_offset = 720
batch_limit = 5
batch_processed = 5
inserted = 2
updated = 0
filtered_out = 3
skipped = 0
errors = 0
next_offset = 725
has_more = true
```

État :

``` text
Pipeline : ✅
Downloader : ✅
Parser : ✅
Filtre : ⚠️ à améliorer
RAG ingestion : ✅
Pagination : ✅
Collection complète : 🔄 à terminer
```

### Prochaine action Knowledge Engine

**Terminer FAO / AGRIS.**

Ne pas retraiter BRAB.

------------------------------------------------------------------------

## 11. Ancien connecteur FAO DSpace

Le connecteur :

``` text
https://openknowledge.fao.org/server/api
```

a retourné :

``` text
HTTP 401
```

Décision : conserver la voie AGRIS ODS fonctionnelle et ne pas revenir
au connecteur DSpace sauf nécessité future.

------------------------------------------------------------------------

## 12. INRAB

Plateformes testées mais actuellement non exploitables :

``` text
https://publications-chercheurs.inrab.bj/
https://technologies.inrab.bj/
https://chercheurs.inrab.bj/
```

BRAB est actuellement la source INRAB exploitable retenue.

Cela ne signifie pas que BRAB contient nécessairement toute la
documentation INRAB.

------------------------------------------------------------------------

## 13. Total actuel Supabase

Endpoint :

``` text
GET /knowledge/count
```

Dernier résultat :

``` json
{
  "documents": 2367
}
```

Attention : 2367 est le total global du stockage de connaissances, pas
le nombre BRAB.

------------------------------------------------------------------------

## 14. main.py --- REFACTORISATION À FAIRE

`main.py` est devenu trop long.

Objectif : en faire un point d'assemblage de l'application plutôt qu'un
fichier contenant toute la logique.

Architecture cible :

``` text
app/
├── main.py
├── api/
│   ├── health.py
│   ├── knowledge.py
│   ├── ai.py
│   ├── webhook.py
│   ├── voice.py
│   └── vision.py
├── knowledge_engine/
├── conversation/
├── voice/
├── vision/
├── languages/
└── ...
```

Le refactoring doit être fait **après stabilisation FAO + filtre**, puis
suivi de tests de non-régression.

Ne pas supprimer les endpoints historiques sans vérifier leur
utilisation.

------------------------------------------------------------------------

## 15. PRODUIT V1 --- priorité

Nous ne voulons plus piloter le projet uniquement par le nombre de
sources documentaires.

Objectif :

**terminer le produit utilisable par le client final.**

Parcours cible :

``` text
Agriculteur
      ↓
WhatsApp
      ↓
Texte / Voix / Image
      ↓
Compréhension
      ↓
Conversation Engine
      ↓
Contexte utilisateur
      ↓
Knowledge Engine / RAG
      ↓
Raisonnement
      ↓
Réponse
      ↓
Texte ou Voix
      ↓
Agriculteur
```

------------------------------------------------------------------------

## 16. Langues V1

Langues :

``` text
Français
Fon
Yoruba
Dendi
```

Le système doit pouvoir :

-   comprendre la langue ;
-   conserver le contexte ;
-   produire une réponse adaptée ;
-   produire une réponse vocale lorsque demandé.

------------------------------------------------------------------------

## 17. Conversation Engine --- À FINALISER

Le système doit combiner :

``` text
question utilisateur
+
historique
+
profil
+
langue
+
contexte agricole
+
résultats RAG
```

pour produire une réponse cohérente.

Chaîne :

``` text
Comprendre
   ↓
Contextualiser
   ↓
Chercher
   ↓
Raisonner
   ↓
Répondre
```

À finaliser :

-   mémoire conversationnelle ;
-   contexte ;
-   profil agriculteur ;
-   langue préférée ;
-   réponses avec sources ;
-   gestion de l'incertitude.

------------------------------------------------------------------------

## 18. Voix --- À FAIRE

Objectif :

``` text
Audio agriculteur
      ↓
Speech-to-Text
      ↓
détection / identification langue
      ↓
Conversation Engine
      ↓
RAG
      ↓
réponse
      ↓
Text-to-Speech
      ↓
Audio
```

À développer :

-   réception audio ;
-   transcription ;
-   identification langue ;
-   traitement conversationnel ;
-   synthèse vocale ;
-   Français ;
-   Fon ;
-   Yoruba ;
-   Dendi ;
-   gestion des erreurs ;
-   tests avec de vrais messages vocaux.

------------------------------------------------------------------------

## 19. Image / Vision --- À FAIRE

Objectif :

``` text
Photo plante / feuille / fruit / ravageur
          +
question utilisateur
          ↓
Vision
          ↓
analyse
          ↓
Knowledge Engine / RAG
          ↓
raisonnement
          ↓
réponse
```

Cas :

-   feuilles jaunissantes ;
-   symptômes ;
-   ravageurs ;
-   maladies ;
-   plantes ;
-   fruits ;
-   dégâts visibles.

Le système doit gérer l'incertitude et ne pas présenter une analyse
visuelle incertaine comme un diagnostic certain.

------------------------------------------------------------------------

## 20. WhatsApp --- À FINALISER

Canal principal V1 :

``` text
WhatsApp
```

Routes présentes :

``` text
GET  /webhook
POST /webhook
```

À finaliser :

-   vérification webhook ;
-   réception texte ;
-   réception audio ;
-   réception image ;
-   réponse texte ;
-   réponse audio ;
-   gestion utilisateurs ;
-   gestion erreurs ;
-   tests multi-utilisateurs.

------------------------------------------------------------------------

## 21. Parcours client final

### Scénario voix

``` text
Agriculteur
→ message vocal en Fon
→ Speech-to-Text
→ compréhension
→ RAG
→ raisonnement
→ réponse en Fon
→ Text-to-Speech
→ message vocal
```

### Scénario image

``` text
Photo feuille
+
question
→ Vision
→ RAG
→ raisonnement
→ réponse
```

### Scénario texte

``` text
Question texte en français
→ RAG
→ réponse française sourcée
```

------------------------------------------------------------------------

## 22. Ordre de travail jusqu'à la V1

### Phase A --- Knowledge Engine

``` text
1. Terminer FAO / AGRIS
2. Corriger AgriculturalRelevanceFilter
3. Ajouter tests de régression
4. Vérifier RAG
```

### Phase B --- Backend

``` text
5. Refactoriser main.py
6. Séparer les routers
7. Nettoyer les endpoints de test historiques
8. Tests de non-régression
```

### Phase C --- Conversation

``` text
9. Finaliser Conversation Engine
10. Mémoire / contexte
11. Profil agriculteur
12. Langues
13. Réponses sourcées
14. Gestion de l'incertitude
```

### Phase D --- Multimodal

``` text
15. Speech-to-Text
16. Text-to-Speech
17. Image / Vision
18. Image + texte
```

### Phase E --- WhatsApp

``` text
19. Texte
20. Voix
21. Image
22. Réponses texte
23. Réponses audio
24. Multi-utilisateurs
```

### Phase F --- Validation V1

``` text
25. Tests bout en bout
26. Tests langues
27. Tests voix
28. Tests images
29. Tests RAG
30. Tests erreurs
31. Tests performance
32. Monitoring
33. Sécurité
34. Démonstration client
```

------------------------------------------------------------------------

## 23. Sources supplémentaires --- APRÈS V1

Une fois la V1 client final terminée :

``` text
V1 client final
      ↓
ITA
      ↓
AfricaRice
      ↓
autres sources
```

Ces sources devront utiliser le pipeline commun.

Ne pas interrompre la finalisation de la V1 pour brancher toutes les
sources possibles.

------------------------------------------------------------------------

## 24. Git / déploiement

Dépôt :

``` text
main
```

Dernier état connu après les corrections :

``` text
working tree clean
branch main
up to date with origin/main
```

Commits importants :

``` text
991fe46
Add agricultural relevance filter to ingestion

beba0d3
Preserve ingestion job errors

be31463
Integrate agricultural relevance filter into RAG ingestion
```

Les corrections Jina et ingestion ont également été poussées avant le
dernier test BRAB.

Procédure :

``` text
python -m compileall app/knowledge_engine
↓
git status
↓
git add
↓
git status
↓
git commit
↓
git push
↓
Render → Live
↓
test production
```

------------------------------------------------------------------------

## 25. Règle de reprise après erreur

``` text
1. Ne pas avancer l'offset.
2. Identifier l'erreur.
3. Corriger uniquement la cause.
4. Compiler.
5. Commit.
6. Push.
7. Attendre Render Live.
8. Relancer le même offset.
9. Vérifier failed/errors.
10. Continuer seulement après succès.
```

Cette règle a déjà été appliquée avec succès lors du timeout BRAB
`offset=120`.

------------------------------------------------------------------------

## 26. Point de reprise actuel

``` text
SikaGlé
│
├── Infrastructure                  ✅
├── Knowledge Engine                ✅
├── Supabase                        ✅
├── Jina                            ✅
├── RAG                             ✅
├── Filtre agricole                 ⚠️ correction à faire
│
├── BRAB                            ✅ 152/152
├── FAO / AGRIS                     🔄 à terminer
├── INRAB                           ⏸ BRAB exploité
│
├── main.py                         ⏳ refactor
├── Conversation Engine             🔄 à finaliser
├── Texte                           🔄
├── Voix                            ⏳
├── Image                           ⏳
├── Français                        🔄
├── Fon                             ⏳
├── Yoruba                          ⏳
├── Dendi                           ⏳
├── WhatsApp                        🔄
│
├── Tests bout en bout              ⏳
└── V1 client final                 ⏳
```

------------------------------------------------------------------------

# 27. PROCHAINE ACTION IMMÉDIATE

**Ne pas recommencer BRAB.**

Ordre immédiat :

``` text
FAO / AGRIS
    ↓
terminer l'ingestion
    ↓
corriger le filtre agricole
    ↓
tests de régression
    ↓
valider le RAG
    ↓
refactor main.py
    ↓
Conversation Engine
    ↓
Voix
    ↓
Image
    ↓
Français / Fon / Yoruba / Dendi
    ↓
WhatsApp
    ↓
tests bout en bout
    ↓
V1 client final
```

ITA, AfricaRice et les autres sources seront rebranchées **après la
V1**.

------------------------------------------------------------------------

# 28. Prompt de reprise pour une nouvelle conversation

Copier ce prompt avec ce document :

> Nous continuons le projet SikaGlé.
>
> Voici le document de continuité officiel du projet.
>
> Utilise-le comme référence principale.
>
> Agis comme architecte du projet : préserve l'architecture existante,
> évite les régressions, vérifie les impacts sur les autres modules et
> guide-moi étape par étape.
>
> Je ne suis pas développeur : donne-moi des instructions concrètes,
> simples et séquentielles. Ne me donne pas plusieurs modifications
> simultanément lorsque cela peut créer de la confusion.
>
> Ne recommence pas les étapes marquées comme terminées.
>
> Notre priorité immédiate est de terminer FAO/AGRIS, puis de corriger
> définitivement le filtre agricole et ses tests.
>
> Ensuite nous refactoriserons main.py, puis nous terminerons le produit
> V1 de bout en bout : texte, voix, image, Français, Fon, Yoruba, Dendi
> et WhatsApp.
>
> Nous ajouterons ITA, AfricaRice et les autres sources seulement après
> la V1.
>
> Commence par lire ce document, résume très brièvement où nous en
> sommes, puis indique-moi **une seule prochaine action concrète**.
