# Architecture de SikaGlé

Version : 1.0

---

# Vision

SikaGlé est un moteur de recherche documentaire basé sur le RAG (Retrieval-Augmented Generation) destiné à centraliser, indexer et interroger des connaissances scientifiques et techniques, principalement dans le domaine agricole.

Le système est conçu pour être :

- modulaire ;
- évolutif ;
- testable ;
- maintenable.

Chaque composant possède une responsabilité unique.

---

# Architecture générale

```
                 FastAPI
                    │
                    ▼
            KnowledgeService
                    │
    ┌───────────────┼────────────────┐
    ▼               ▼                ▼
 Ingestion         RAG         Administration
    │               │
    ▼               ▼
Connecteurs    Retrieval Engine
    │               │
    ▼               ▼
Downloader     Embeddings
    │               │
    ▼               ▼
Processing ───► Validation ───► Vector Store
```

---

# Modules

## API

Responsabilité :

- exposer les endpoints REST ;
- valider les requêtes ;
- retourner les réponses.

Le module API ne contient aucune logique métier.

---

## KnowledgeService

Responsabilité :

- coordonner les opérations ;
- appeler les composants spécialisés.

Le service ne réalise aucun traitement directement.

---

## Ingestion

Responsabilité :

- découvrir les documents ;
- télécharger les fichiers ;
- lancer l'indexation ;
- produire un rapport d'exécution.

Le moteur d'ingestion ne connaît ni Gemini ni ChromaDB.

---

## Connecteurs

Responsabilité :

communiquer avec une source documentaire.

Exemples :

- BRAB
- INRAB
- FAO
- AGRIS
- HAL

Tous les connecteurs héritent de BaseConnector.

Chaque connecteur retourne des objets DocumentMetadata.

---

## Downloader

Responsabilité :

télécharger les documents.

Le Downloader ne connaît pas la source documentaire.

Il reçoit uniquement une URL.

---

## Processing

Responsabilité :

transformer un document PDF en texte exploitable.

Pipeline :

PDF

↓

Extraction

↓

Nettoyage

↓

Chunking

↓

Validation

---

## Validation

Responsabilité :

vérifier qu'un document est exploitable.

Exemples :

- texte vide ;
- nombre de caractères insuffisant ;
- aucun chunk produit.

Un document invalide n'est jamais indexé.

---

## Embeddings

Responsabilité :

transformer les chunks en vecteurs.

Le module utilise Gemini Embedding.

---

## Vector Store

Responsabilité :

stocker les embeddings.

Le moteur actuel utilise ChromaDB.

---

## Retrieval

Responsabilité :

retrouver les passages les plus pertinents.

Le moteur retournera :

- les chunks ;
- les métadonnées ;
- les scores.

---

## Prompt Builder

Responsabilité :

assembler le contexte envoyé au LLM.

Le Prompt Builder ne connaît pas Gemini.

---

## LLM

Responsabilité :

générer la réponse finale.

Le moteur actuel utilise Gemini.

---

# Principes d'architecture

## 1. Une classe = une responsabilité

Chaque classe accomplit une seule tâche.

---

## 2. Dépendances descendantes

Les dépendances vont toujours vers les couches inférieures.

API

↓

Service

↓

Ingestion

↓

Connecteurs

Jamais l'inverse.

---

## 3. Isolation des modules

Les modules ne doivent pas connaître l'implémentation interne des autres modules.

Exemple :

Le Downloader ignore BRAB.

Le Connecteur ignore ChromaDB.

Le Processing ignore Gemini.

---

## 4. Interfaces stables

Les échanges entre modules utilisent des objets métier clairement définis.

Exemple :

- DocumentMetadata
- ValidationResult
- ProcessingResult
- IngestionReport

---

## 5. Tolérance aux erreurs

Une erreur sur un document ne doit jamais interrompre l'indexation complète d'une source.

---

## 6. Extensibilité

L'ajout d'une nouvelle source documentaire ne doit nécessiter que :

- un nouveau connecteur ;
- son enregistrement dans le registre.

Aucun autre composant ne doit être modifié.

---

# Arborescence cible

```
app/

├── api/
├── core/
├── knowledge_engine/
│
├── connectors/
├── downloader/
├── extraction/
├── processing/
├── validation/
├── embeddings/
├── vectorstore/
├── retrieval/
├── prompting/
├── ingestion/
├── generation/
│
└── services/

docs/

tests/
```

---

# Objectifs

À terme, SikaGlé devra permettre :

- l'indexation de plusieurs bibliothèques scientifiques ;
- la mise à jour incrémentale des connaissances ;
- la recherche hybride (vectorielle + mots-clés) ;
- la citation des sources utilisées ;
- la supervision complète du moteur d'ingestion.

---

# Philosophie

Le projet privilégie :

- la simplicité ;
- la lisibilité ;
- la modularité ;
- la robustesse.

Chaque évolution doit renforcer ces principes.
