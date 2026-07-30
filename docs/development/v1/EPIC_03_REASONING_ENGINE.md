# EPIC_03_REASONING_ENGINE.md

# SikaGlé

# EPIC 03 — Reasoning Engine

**Epic ID :** EPIC-03

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★★ (Critique)

**Responsable :** Reasoning Engine

---

# 1. Objectif

Construire le moteur de raisonnement agricole de SikaGlé.

Le Reasoning Engine analyse une demande, identifie les informations utiles, détecte les informations manquantes, construit des hypothèses, orchestre les recherches documentaires et prépare un plan de réponse.

Il ne génère pas directement la réponse finale.

Son rôle est de guider l'ensemble du processus décisionnel.

---

# 2. Pourquoi un moteur de raisonnement ?

Un chatbot classique fonctionne ainsi :

Question

↓

LLM

↓

Réponse

Cette approche est insuffisante pour un assistant agricole.

SikaGlé suit un processus différent.

```
Question

↓

Compréhension

↓

Extraction des informations

↓

Analyse

↓

Construction d'hypothèses

↓

Recherche documentaire

↓

Analyse des résultats

↓

Planification de la réponse

↓

LLM

↓

Réponse finale
```

Le raisonnement est contrôlé par SikaGlé.

Le LLM n'est plus le décideur.

---

# 3. Valeur métier

Le Reasoning Engine permet :

- d'éviter les réponses précipitées ;
- de demander des informations complémentaires ;
- d'améliorer la pertinence des recherches ;
- de produire des recommandations cohérentes ;
- de réduire les hallucinations.

---

# 4. Personas concernés

Tous les personas.

Le niveau de détail des réponses pourra varier selon le profil, mais le raisonnement restera identique.

---

# 5. Architecture

```
Conversation Context

↓

Intent Detection

↓

Information Extraction

↓

Crop Detection

↓

Symptom Extraction

↓

Missing Information Detection

↓

Hypothesis Builder

↓

Retrieval Planner

↓

Knowledge Engine

↓

Evidence Analyzer

↓

Response Planner

↓

LLM

↓

Response Builder
```

---

# 6. Structure du module

```
reasoning/

models/

services/

strategies/

extractors/

validators/

planners/

prompts/

utils/

reasoner.py

intent_detector.py

crop_detector.py

symptom_extractor.py

context_analyzer.py

missing_information.py

hypothesis_engine.py

retrieval_planner.py

evidence_analyzer.py

response_planner.py
```

---

# 7. Pipeline de raisonnement

Chaque requête suit exactement les mêmes étapes.

### Étape 1

Comprendre la demande.

Questions :

- Que veut l'utilisateur ?
- Quel est son objectif ?

---

### Étape 2

Identifier l'intention.

Exemples :

- diagnostic
- prévention
- traitement
- calendrier
- irrigation
- fertilisation

---

### Étape 3

Identifier la culture.

Exemples :

- maïs
- riz
- manioc
- soja
- tomate

---

### Étape 4

Extraire les symptômes.

Exemples :

- feuilles jaunes
- taches
- flétrissement
- insectes
- fruits noirs

---

### Étape 5

Construire le contexte.

Le moteur rassemble :

- météo
- saison
- localisation
- historique
- mémoire utilisateur

---

### Étape 6

Détecter les informations manquantes.

Exemple :

L'utilisateur dit :

> "Mon maïs est jaune."

Informations manquantes :

- âge de la culture
- localisation
- pluie récente
- parties touchées
- évolution

Le moteur prépare les questions.

---

### Étape 7

Construire plusieurs hypothèses.

Exemple :

Hypothèse A

Carence en azote

Hypothèse B

Stress hydrique

Hypothèse C

Maladie foliaire

Le moteur ne choisit pas immédiatement.

---

### Étape 8

Préparer la recherche documentaire.

Le moteur construit plusieurs requêtes.

Exemple :

```
culture=maïs

symptômes=feuilles jaunes

saison=pluvieuse

localisation=Atlantique
```

---

### Étape 9

Analyser les preuves.

Le Knowledge Engine retourne plusieurs documents.

Le moteur :

- compare ;
- classe ;
- élimine ;
- fusionne.

---

### Étape 10

Construire un plan de réponse.

Le plan contient :

- résumé
- hypothèse principale
- hypothèses secondaires
- niveau de confiance
- recommandations
- sources

Le LLM reçoit uniquement ce plan.

---

# 8. Features

---

## FE-301

Intent Detection

---

## FE-302

Crop Detection

---

## FE-303

Symptom Extraction

---

## FE-304

Context Analyzer

---

## FE-305

Missing Information Detector

---

## FE-306

Hypothesis Engine

---

## FE-307

Retrieval Planner

---

## FE-308

Evidence Analyzer

---

## FE-309

Response Planner

---

## FE-310

Confidence Estimator

---

# 9. User Stories

## US-301

En tant que Coffi,

je veux que SikaGlé me pose des questions complémentaires,

afin d'éviter un mauvais diagnostic.

---

## US-302

En tant qu'Aïcha,

je veux que les recommandations tiennent compte de ma culture et de ma région.

---

## US-303

En tant que Rodrigue,

je veux connaître les hypothèses retenues et les sources utilisées.

---

## US-304

En tant qu'institution,

je veux des réponses cohérentes et explicables.

---

# 10. Données manipulées

Entrées :

- texte
- audio transcrit
- image (V2)
- contexte utilisateur

Sorties :

- hypothèses
- requêtes documentaires
- plan de réponse
- niveau de confiance

---

# 11. Dépendances

Le moteur dépend de :

- Conversation Engine
- Knowledge Platform
- Agricultural Context

Le moteur fournit ensuite le plan au :

- Response Builder

---

# 12. Critères d'acceptation

Le système doit :

✓ détecter l'intention

✓ détecter la culture

✓ détecter les symptômes

✓ construire plusieurs hypothèses

✓ identifier les informations manquantes

✓ préparer la recherche

✓ analyser les preuves

✓ produire un plan de réponse

✓ estimer un niveau de confiance

---

# 13. Tests

Tests unitaires :

- détecteurs
- extracteurs
- planificateurs
- validateurs

Tests d'intégration :

Conversation

↓

Reasoning

↓

Knowledge

↓

Response

Tests métier :

Comparer les décisions du moteur avec les recommandations d'experts agronomes sur un ensemble de cas de référence.

---

# 14. Évolutions V2

- raisonnement multimodal (texte + image) ;
- prise en compte des séries temporelles ;
- apprentissage à partir des retours utilisateurs ;
- règles agronomiques spécifiques par culture ;
- moteur de recommandations proactives.

---

# 15. Définition de terminé

Cette Epic sera terminée lorsque le moteur sera capable de :

- analyser une demande agricole ;
- identifier les informations disponibles ;
- détecter les informations manquantes ;
- construire des hypothèses ;
- préparer les recherches ;
- analyser les résultats ;
- produire un plan de réponse structuré et explicable.

---

# 16. Vision

Le Reasoning Engine est le cerveau de SikaGlé.

Il transforme des informations dispersées en une stratégie de résolution de problème.

Grâce à lui, le système ne se contente pas de répondre à une question : il raisonne comme un conseiller agricole, en s'appuyant sur les connaissances scientifiques, le contexte de l'utilisateur et des preuves documentaires.

Il constitue l'élément différenciant majeur de SikaGlé par rapport aux assistants conversationnels généralistes.

Reasoning Engine
│
├── Intent State
├── Crop State
├── Symptom State
├── Context State
├── Hypothesis State
├── Evidence State
├── Decision State
└── Response State
