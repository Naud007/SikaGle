# SikaGlé — Knowledge Engine
## Document de continuité et guide d'ajout de sources

> Document de référence pour reprendre le travail dans une nouvelle conversation.
> Décrit l'état réel, les décisions d'architecture, les sources validées et le processus d'ajout d'une nouvelle source.

---

## 1. Objectif

Le Knowledge Engine de SikaGlé permet de découvrir des documents, les parser, filtrer les contenus hors domaine agricole, générer des embeddings de dimension **1024**, les stocker dans **Supabase / `knowledge_embeddings`**, puis les exploiter avec le moteur RAG.

Sources prévues :
- BRAB
- FAO / AGRIS
- INRAB
- ITA
- AfricaRice
- autres sources agricoles pertinentes

---

## 2. Architecture générale

```text
SOURCE DOCUMENTAIRE
        ↓
Découverte / catalogue
        ↓
Parser / normalisation
        ↓
DocumentMetadata
        ↓
AgriculturalRelevanceFilter
        ↓
RAGIngestion
        ↓
Construction du texte RAG
        ↓
Embedding 1024D
        ↓
Supabase
        ↓
knowledge_embeddings
        ↓
HybridRetriever
        ↓
RAGService
        ↓
Réponse SikaGlé + sources
```

Le filtre agricole intervient **avant la génération d'embedding**.

---

## 3. Stockage vectoriel

Table :

```text
knowledge_embeddings
```

Colonnes importantes :

```text
id
document_id
chunk_index
chunk_count
content
embedding
title
source
identifier
url
author
published_at
language
document_type
publisher
crop
culture
keywords
country
zone_geographique
created_at
```

L'embedding est :

```text
vector(1024)
```

---

## 4. Recherche vectorielle

Fonction SQL :

```text
public.match_knowledge_embeddings(
    query_embedding vector,
    match_threshold double precision DEFAULT 0.20,
    match_count integer DEFAULT 5
)
```

Similarité :

```sql
1 - (ke.embedding <=> query_embedding)
```

---

## 5. RAG

Chaîne :

```text
RAGService
    ↓
HybridRetriever
    ↓
VectorRetriever
    ↓
GeminiEmbeddingService
    ↓
KnowledgeRepository
    ↓
Supabase
```

Endpoint :

```text
POST /knowledge/ask
```

Test validé avec :

```text
Quels sont les effets du changement climatique sur l'agriculture au Bénin ?
```

Résultat validé :
- `success = true`
- `chunks_used = 5`
- source BRAB
- réponse fondée sur `Effects and trend of climate change in Bénin`

---

# 6. BRAB

## État

```text
Pipeline : ✅
Découverte : ✅
Téléchargement : ✅
Parsing : ✅
Indexation : ✅
RAG : ✅
Test question/réponse : ✅
Collection complète : ⏳
```

BRAB est actuellement notre source INRAB active et exploitable.

**Important :** le pipeline BRAB est validé, mais toute la collection n'est pas encore considérée comme entièrement ingérée.

---

# 7. FAO / AGRIS

## Pipeline fonctionnel

Le pipeline FAO utilisé pour le RAG est le pipeline AGRIS ODS :

```text
AGRIS.ODS.xml
        ↓
datasets AGRIS
        ↓
AGRIS.ODS.BRI.xml
        ↓
FAODatasetParser
        ↓
RAGIngestion
        ↓
AgriculturalRelevanceFilter
        ↓
embedding 1024D
        ↓
Supabase
```

Catalogue :

```text
https://agris.fao.org/ods/AGRIS.ODS.xml
```

Dataset déjà testé :

```text
AGRIS.ODS.BRI.xml
```

Statistiques observées :

```text
datasets_found = 1235
documents_parsed = 784
```

## Test réel du filtre

Test :

```text
dataset_limit = 1
rag_limit = 5
```

Résultat validé :

```text
batch_processed = 5
inserted = 2
filtered_out = 3
updated = 0
skipped = 0
errors = 0
next_offset = 725
has_more = true
```

Donc :

```text
5 documents
├── 2 conservés → embedding → Supabase
└── 3 filtrés → aucun embedding
```

La pagination fonctionne.

**La collection FAO/AGRIS complète reste à poursuivre.**

---

# 8. Ancien connecteur FAO DSpace

Fichier :

```text
app/knowledge_engine/connectors/fao.py
```

Il utilise :

```text
https://openknowledge.fao.org/server/api
```

L'appel :

```text
/server/api/core/items
```

a retourné :

```text
HTTP 401
```

Erreur :

```text
401 Client Error: 401 for url:
https://openknowledge.fao.org/server/api/core/items?size=20
```

## Décision

Ne pas utiliser cette voie pour le pipeline FAO/AGRIS.

Conserver le pipeline AGRIS ODS fonctionnel.

---

# 9. INRAB

Anciennes plateformes identifiées :

```text
https://publications-chercheurs.inrab.bj/
https://technologies.inrab.bj/
https://chercheurs.inrab.bj/
```

Elles sont actuellement problématiques/inaccessibles dans notre environnement.

Le BRAB est une publication de l'INRAB et constitue actuellement la source INRAB exploitable.

## Décision

Pour le moment :

```text
INRAB
   ↓
BRAB
```

Nous ne créons pas de connecteur INRAB séparé dépendant des anciennes plateformes.

Cela ne signifie pas que toute la documentation INRAB est nécessairement dans BRAB ; cela signifie seulement que BRAB est la source INRAB active retenue actuellement.

---

# 10. AgriculturalRelevanceFilter

Fichier :

```text
app/knowledge_engine/filters/agricultural_relevance.py
```

Méthodes importantes :

```python
analyze(document)
is_relevant(document)
```

`analyze()` retourne un résultat contenant :

```text
relevant
score
reason
```

Exemples validés :

```text
Effects and trend of climate change in Bénin
→ True

FOOT REFLEXOLOGY MASSAGE IN OLDER WOMEN
→ False

DISSEMINATION AND POPULARIZATION OF ASTRONOMY...
→ False

DISSEMINATION OF THE BEHAVIOR ANALYSIS...
→ False

NUTRITIONAL AMBULATORY CARE...
→ False

Integrated soil fertility management for maize production
→ True

Cassava production and pest management
→ True

Improving soil fertility in West Africa
→ True

Climate variability and rice yields
→ True

Livestock feeding systems in Benin
→ True

Irrigation water management for maize
→ True
```

Le matching utilise des frontières de mots afin d'éviter les faux positifs de sous-chaînes comme :

```text
POPULARIZATION
```

qui ne doit pas être interprété comme contenant :

```text
agriculture
```

---

# 11. RAGIngestion

Fichier :

```text
app/knowledge_engine/storage/rag_ingestion.py
```

Le filtre est intégré avant l'embedding :

```text
document
    ↓
normalize_document()
    ↓
relevance_filter.analyze(document)
    ↓
False → filtered_out += 1 → continue
    ↓
True
    ↓
build_rag_text()
    ↓
generate_document_embedding()
    ↓
dimension 1024
    ↓
Supabase
```

Le résultat contient :

```text
filtered_out
```

## Pagination

```python
batch = documents[offset:offset + limit]
```

puis :

```text
next_offset = offset + len(batch)
```

Un document filtré compte donc dans le batch consommé.

Exemple :

```text
5 documents
2 indexés
3 filtrés
next_offset = offset + 5
```

Cela évite de retraiter indéfiniment les documents rejetés.

---

# 12. Ingestion et erreurs

Composants :

```text
IngestionManager
SourceIngestor
IngestionReport
GlobalIngestionReport
IngestionJob
```

`IngestionJob` conserve maintenant :

```python
error: str | None
```

et `fail(reason)` sauvegarde l'erreur.

Cela permet de diagnostiquer une ingestion échouée.

---

# 13. Endpoints importants

Sources :

```text
GET /knowledge/sources
```

Retour actuel :

```text
brab
fao
inrab
```

RAG :

```text
POST /knowledge/ask
```

Tests AGRIS :

```text
GET /knowledge/fao-ods-structure
GET /knowledge/fao-ods-test
GET /knowledge/fao-parser-test
GET /knowledge/fao-datasets-test
GET /knowledge/fao-dataset-parser-test
GET /knowledge/fao-rag-pipeline-test
GET /knowledge/fao-dataset-pipeline-test
GET /knowledge/rag-ingestion-test
GET /knowledge/rag-ingest
```

Pipeline AGRIS validé :

```text
GET /knowledge/fao-dataset-pipeline-test
```

Paramètres exposés :

```text
dataset_limit
rag_limit
```

Test validé :

```text
dataset_limit = 1
rag_limit = 5
```

---

# 14. Procédure pour une nouvelle source

Toujours suivre cet ordre.

### 1. Étudier la source

Identifier :
- site officiel ;
- catalogue ;
- API ;
- XML/ODS/CSV ;
- pages de publications ;
- URLs PDF ;
- pagination ;
- authentification éventuelle.

### 2. Tester l'accès

Obtenir :
- HTTP 200 ;
- contenu non vide ;
- taille cohérente.

### 3. Créer le downloader/client si nécessaire

### 4. Créer le parser

Normaliser autant que possible :

```text
title
content
source
identifier
url
author
published_at
language
document_type
publisher
crop
culture
keywords
country
zone_geographique
```

### 5. Tester le parser

Utiliser quelques documents.

### 6. Passer par le filtre

Toujours :

```python
AgriculturalRelevanceFilter.analyze(document)
```

avant l'embedding.

### 7. Passer par RAGIngestion

Ne pas dupliquer le pipeline embedding/Supabase pour chaque source sans nécessité.

### 8. Tester un petit batch

Commencer par :

```text
1 dataset
5 documents
```

ou le plus petit équivalent.

### 9. Vérifier

```text
batch_processed
inserted
updated
filtered_out
skipped
errors
next_offset
has_more
```

### 10. Tester le RAG

Poser une vraie question agricole et vérifier :
- pertinence ;
- source ;
- chunks utilisés ;
- absence de contenu hors domaine.

### 11. Seulement ensuite lancer l'ingestion complète.

---

# 15. Git / déploiement

Avant commit :

```bash
python -m compileall app/knowledge_engine
```

Puis :

```bash
git status
```

Vérifier les fichiers modifiés.

Ensuite :

```bash
git add <fichiers>
git status
git commit -m "Message clair"
git push
```

Attendre :

```text
Render → Live
```

puis tester en production.

---

# 16. Commits importants

Filtre agricole :

```text
991fe46
Add agricultural relevance filter to ingestion
```

Conservation des erreurs :

```text
beba0d3
Preserve ingestion job errors
```

Intégration du filtre dans RAG :

```text
be31463
Integrate agricultural relevance filter into RAG ingestion
```

Ces commits sont sur `main`.

---

# 17. État actuel

| Source | Pipeline | Tests | Collection complète |
|---|---|---|---|
| BRAB | ✅ | ✅ | ⏳ |
| FAO / AGRIS | ✅ | ✅ | ⏳ |
| INRAB | couvert actuellement par BRAB | ✅ | — |
| ITA | ⏳ | — | — |
| AfricaRice | ⏳ | — | — |

**BRAB et FAO ne sont donc pas encore terminés au niveau de l'ingestion complète.**

---

# 18. Prochaines tâches

Ordre recommandé :

```text
1. Poursuivre/terminer ingestion BRAB
2. Poursuivre/terminer ingestion FAO/AGRIS
3. Documenter les résultats finaux
4. Intégrer ITA
5. Intégrer AfricaRice
6. Ajouter d'autres sources si nécessaire
```

Une source n'est considérée comme pleinement validée qu'après :
- pipeline fonctionnel ;
- petit batch réussi ;
- filtre validé ;
- embeddings valides ;
- indexation Supabase valide ;
- test RAG ;
- documentation.

---

# 19. Continuité entre conversations

Si une nouvelle conversation est nécessaire, fournir ce fichier et écrire :

> Voici le document de continuité du Knowledge Engine de SikaGlé. Utilise-le comme référence principale. Ne recommence pas les étapes déjà validées. Vérifie l'état indiqué dans « État actuel » et reprends à « Prochaines tâches ».

Mettre ce document à jour après chaque grande décision ou intégration.

---

# 20. Règle architecturale principale

Le principe à préserver :

```text
SOURCE
  ↓
CONNECTEUR / DOWNLOADER
  ↓
PARSER
  ↓
DocumentMetadata
  ↓
AgriculturalRelevanceFilter
  ↓
RAGIngestion
  ↓
Embedding 1024D
  ↓
Supabase
```

Une nouvelle source doit s'adapter à cette architecture.

**Le pipeline RAG commun ne doit pas être dupliqué pour chaque source.**
