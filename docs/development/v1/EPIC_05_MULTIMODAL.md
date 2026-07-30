# EPIC_05_MULTIMODAL.md

# SikaGlé

# EPIC 05 — Multimodal Engine

**Epic ID :** EPIC-05

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★★

**Responsable :** Multimodal Engine

---

# 1. Objectif

Construire un moteur multimodal permettant à SikaGlé de comprendre et produire différents types de contenus.

Pour la V1, les modalités supportées sont :

- texte
- audio

L'architecture doit toutefois être conçue dès aujourd'hui pour accueillir :

- images
- vidéos
- documents

sans refonte majeure.

Le Multimodal Engine agit comme une couche de traduction entre les différents formats d'entrée/sortie et le reste du système.

---

# 2. Valeur métier

Le Multimodal Engine permet à tous les agriculteurs, quel que soit leur niveau d'alphabétisation, d'utiliser SikaGlé.

Il garantit que :

- un message vocal est traité comme un message texte ;
- une réponse textuelle peut être restituée sous forme audio ;
- le moteur de raisonnement travaille toujours avec un format unifié.

---

# 3. Personas concernés

## Principalement

- Coffi

## Également

- Aïcha
- Rodrigue
- Institutions
- Entrepreneur Agricole

---

# 4. Architecture

```
Utilisateur

↓

Canal

↓

Input Router

↓

Input Processor

↓

Normalizer

↓

Conversation Engine

↓

Reasoning Engine

↓

Response Builder

↓

Output Generator

↓

Canal
```

---

# 5. Structure du module

```
multimodal/

models/

services/

processors/

speech/

text/

image/

translation/

normalization/

routing/

builders/
```

---

# 6. Responsabilités

Le Multimodal Engine est responsable de :

- détecter le type de contenu ;
- convertir les contenus ;
- normaliser les données ;
- produire les sorties adaptées au canal.

Il ne réalise aucun raisonnement.

---

# 7. Fonctionnalités

---

## FE-501 — Input Router

Déterminer automatiquement le type d'entrée.

Types supportés :

- texte
- audio

Prévu V2 :

- image
- vidéo
- document

---

## FE-502 — Speech To Text

Transformer un message vocal en texte.

Le résultat est transmis au Conversation Engine.

---

## FE-503 — Text To Speech

Transformer une réponse textuelle en audio.

Le moteur choisit automatiquement :

- la langue
- la voix
- la vitesse

---

## FE-504 — Language Detection

Détecter automatiquement :

- français
- fon
- yoruba

L'architecture doit permettre l'ajout de nouvelles langues.

---

## FE-505 — Translation Layer

Le moteur traduit si nécessaire.

Exemple :

```
Fon

↓

Français interne

↓

Reasoning Engine

↓

Français interne

↓

Fon
```

Le moteur de raisonnement ne travaille qu'avec une langue pivot.

---

## FE-506 — Content Normalizer

Créer une représentation unique des contenus.

Quel que soit le canal :

```
Audio

↓

Texte

↓

NormalizedMessage

↓

Conversation Engine
```

---

## FE-507 — Output Generator

Créer automatiquement la meilleure réponse.

Exemple :

Entrée :

Audio

↓

Réponse :

Audio

Entrée :

Texte

↓

Réponse :

Texte

---

# 8. User Stories

---

## US-501

En tant que Coffi,

je veux envoyer un message vocal,

afin d'utiliser SikaGlé sans écrire.

---

## US-502

En tant que Coffi,

je veux recevoir une réponse vocale,

afin de ne pas avoir à lire.

---

## US-503

En tant qu'Aïcha,

je veux continuer à utiliser les messages texte.

---

## US-504

En tant qu'utilisateur,

je veux que SikaGlé comprenne automatiquement la langue utilisée.

---

# 9. Modèle conceptuel

```
Input

↓

Media Type

↓

Processor

↓

Normalizer

↓

Conversation

↓

Reasoning

↓

Response

↓

Output Generator

↓

Output
```

---

# 10. Données manipulées

## Entrées

- texte
- audio

## Sorties

- texte
- audio

## V2

- image
- vidéo
- document

---

# 11. Dépendances

Cette Epic dépend de :

- Conversation Engine
- Reasoning Engine

Elle est utilisée par :

- WhatsApp Platform
- API
- Applications mobiles
- Interface Web

---

# 12. Critères d'acceptation

Le système doit être capable de :

✓ reconnaître le type d'entrée

✓ convertir un audio en texte

✓ détecter automatiquement la langue

✓ normaliser les contenus

✓ produire un texte

✓ produire un audio

✓ sélectionner automatiquement le bon format de sortie

---

# 13. Tests

## Unitaires

- Input Router
- Speech To Text
- Text To Speech
- Language Detector
- Translator
- Normalizer

---

## Intégration

Audio

↓

Speech To Text

↓

Conversation

↓

Reasoning

↓

Réponse

↓

Text To Speech

↓

Audio

---

## Tests métier

Comparer :

- qualité de transcription ;
- fidélité de traduction ;
- qualité de synthèse vocale ;
- temps de traitement.

---

# 14. Évolutions V2

- reconnaissance d'images agricoles ;
- analyse de feuilles ;
- détection de maladies sur photos ;
- vidéos courtes ;
- OCR de documents agricoles ;
- reconnaissance d'étiquettes de pesticides ;
- génération de résumés audio.

---

# 15. Définition de terminé

Cette Epic sera terminée lorsque :

- un message vocal pourra être traité de bout en bout ;
- une réponse pourra être renvoyée sous forme audio ;
- les langues supportées seront détectées automatiquement ;
- tous les traitements utiliseront un format normalisé commun ;
- les tests fonctionnels seront validés.

---

# 16. Vision

Le Multimodal Engine garantit que les capacités de SikaGlé restent indépendantes du format utilisé par l'utilisateur.

Qu'un agriculteur écrive, parle ou, demain, envoie une photo de sa culture, le reste du système continuera à fonctionner selon le même processus.

Cette couche constitue la fondation de l'accessibilité de SikaGlé et prépare l'arrivée des futures capacités multimodales des versions V2 à V5.



NormalizedMessage
│
├── message_id
├── conversation_id
├── user_id
├── channel
├── modality
├── detected_language
├── normalized_text
├── original_content
├── attachments
├── metadata
└── timestamp
