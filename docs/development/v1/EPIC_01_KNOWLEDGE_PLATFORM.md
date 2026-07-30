# EPIC_01_KNOWLEDGE_PLATFORM.md

# SikaGlé

# EPIC 01 — Knowledge Platform

**Epic ID :** EPIC-01

**Version :** V1

**Statut :** En cours (≈90%)

**Priorité :** Faible

**Responsable :** Knowledge Engine

---

# 1. Objectif

Construire une plateforme documentaire capable de transformer des publications agricoles en une base de connaissances exploitable par le moteur de raisonnement.

Cette plateforme constitue le socle de toutes les réponses générées par SikaGlé.

Elle doit garantir :

- des connaissances fiables ;
- des recherches rapides ;
- des sources vérifiables ;
- une évolution simple de la base documentaire.

---

# 2. Valeur métier

Cette Epic permet à SikaGlé de répondre à des questions agricoles en s'appuyant sur des documents scientifiques plutôt que sur les seules connaissances du modèle de langage.

Sans cette plateforme, le système ne peut garantir :

- la qualité des réponses ;
- la traçabilité des informations ;
- la mise à jour des connaissances.

---

# 3. Personas concernés

## Principalement

- Rodrigue
- Institution

---

## Indirectement

- Coffi
- Aïcha
- Entrepreneur Agricole

Tous les utilisateurs bénéficient des connaissances produites par cette plateforme.

---

# 4. Architecture

```
Documents

↓

Connectors

↓

Downloader

↓

Cleaning

↓

Chunking

↓

Embeddings

↓

Vector Store

↓

Search

↓

RAG

↓

Reasoning Engine
```

---

# 5. Modules

```
knowledge_engine/

connectors/

ingestion/

chunking/

embeddings/

repositories/

vectorstores/

retrieval/

rag/

metadata/

reports/
```

---

# 6. Fonctionnalités

## FE-101 — Connecteurs

### Objectif

Importer des documents depuis plusieurs sources.

### Sources prévues

- PDF locaux
- URL
- Sites institutionnels
- Bases documentaires
- API partenaires

---

## FE-102 — Téléchargement

Téléchargement fiable.

Fonctionnalités :

- retry
- timeout
- validation
- rapports d'erreurs

---

## FE-103 — Nettoyage

Suppression :

- doublons
- caractères inutiles
- contenus vides

Normalisation des documents.

---

## FE-104 — Chunking

Découpage intelligent.

Objectifs :

- préserver le contexte ;
- optimiser la recherche ;
- améliorer le RAG.

---

## FE-105 — Embeddings

Création des représentations vectorielles.

Chaque chunk est vectorisé.

---

## FE-106 — Base vectorielle

Stockage :

- embeddings
- métadonnées
- documents
- index

---

## FE-107 — Recherche hybride

Combinaison :

- recherche vectorielle
- recherche par mots-clés

Puis :

re-ranking.

---

## FE-108 — Repository

Couche d'abstraction entre le moteur de recherche et la base vectorielle.

Objectifs :

- indépendance ;
- testabilité ;
- évolutivité.

---

## FE-109 — RAG

Construction du contexte documentaire.

Le RAG fournit :

- les passages pertinents ;
- les sources ;
- les métadonnées.

---

## FE-110 — Reporting

Production de rapports d'ingestion.

Statistiques :

- documents
- erreurs
- doublons
- chunks
- temps

---

# 7. État actuel

## Déjà implémenté

✅ Connecteurs

✅ Téléchargement

✅ Chunking

✅ Embeddings

✅ ChromaDB

✅ Search Engine

✅ Hybrid Search

✅ Vector Retriever

✅ Keyword Retriever

✅ Hybrid Retriever

✅ RAG Service

✅ Repository

✅ Reports

---

## Partiellement implémenté

🟡 Métadonnées enrichies

🟡 Optimisation des recherches

🟡 Gestion avancée des erreurs

---

## À développer

- nouveaux connecteurs ;
- filtres plus avancés ;
- optimisation des performances ;
- cache documentaire ;
- monitoring de l'ingestion.

---

# 8. User Stories

---

## US-101

En tant qu'agronome,

je veux que SikaGlé recherche dans plusieurs centaines de documents,

afin d'obtenir des réponses fiables.

---

## US-102

En tant que producteur,

je veux que les réponses soient basées sur des documents réels,

afin de leur faire confiance.

---

## US-103

En tant qu'administrateur,

je veux ajouter facilement de nouveaux documents,

afin d'enrichir les connaissances.

---

# 9. Dépendances

Cette Epic ne dépend d'aucune autre.

En revanche :

Conversation Engine

↓

Reasoning Engine

↓

Weather Engine

↓

Analytics

↓

API

dépendent directement de la Knowledge Platform.

---

# 10. Critères d'acceptation

Le système doit être capable de :

✓ importer des documents

✓ nettoyer les contenus

✓ détecter les doublons

✓ créer les chunks

✓ générer les embeddings

✓ stocker les vecteurs

✓ rechercher efficacement

✓ retourner les meilleures sources

✓ produire un contexte documentaire

---

# 11. Tests

## Unitaires

- Connecteurs
- Chunking
- Embeddings
- Repository
- Retrieval

---

## Intégration

Pipeline complet :

Document

↓

Ingestion

↓

Chunking

↓

Embedding

↓

Recherche

↓

RAG

---

## Performance

Mesurer :

- temps d'ingestion ;
- temps de recherche ;
- mémoire ;
- taille des index.

---

# 12. Améliorations futures (V2+)

- OCR pour les PDF scannés ;
- extraction de tableaux ;
- extraction d'images et légendes ;
- recherche multilingue ;
- indexation incrémentale ;
- recherche fédérée sur plusieurs bases documentaires.

---

# 13. Définition de terminé

Cette Epic sera considérée comme terminée lorsque :

- tous les connecteurs prévus pour V1 fonctionneront ;
- les documents seront correctement indexés ;
- la recherche hybride sera stable ;
- le RAG fournira des sources pertinentes ;
- les performances respecteront les objectifs ;
- les tests seront automatisés ;
- la documentation technique sera complète.

---

# 14. Risques

- documents mal structurés ;
- PDF de mauvaise qualité ;
- duplication des données ;
- temps d'indexation élevé ;
- évolution des formats de documents.

Des mécanismes de validation et de surveillance devront limiter ces risques.

---

# Conclusion

La Knowledge Platform est le fondement documentaire de SikaGlé.

Même si cette Epic est déjà largement réalisée, elle reste un composant stratégique qui devra évoluer en permanence pour enrichir la base de connaissances, améliorer la qualité des recherches et soutenir les futurs moteurs de raisonnement et d'analyse.

Aucune réponse de SikaGlé ne peut être plus fiable que les connaissances mises à disposition par cette plateforme.
