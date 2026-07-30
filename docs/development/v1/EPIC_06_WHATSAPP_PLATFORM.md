# EPIC_06_WHATSAPP_PLATFORM.md

# SikaGlé

# EPIC 06 — WhatsApp Platform

**Epic ID :** EPIC-06

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★★

**Responsable :** WhatsApp Platform

---

# 1. Objectif

Construire la plateforme officielle d'interaction entre les utilisateurs et SikaGlé via WhatsApp.

La plateforme est responsable de :

- recevoir les messages ;
- traiter les événements WhatsApp ;
- convertir les médias en objets normalisés ;
- transmettre les requêtes au Conversation Engine ;
- envoyer les réponses aux utilisateurs.

Elle constitue la principale interface utilisateur de la V1.

---

# 2. Valeur métier

WhatsApp est le premier canal de diffusion de SikaGlé.

L'utilisateur ne connaît ni l'API, ni le moteur de raisonnement.

Pour lui :

```
WhatsApp

=

SikaGlé
```

La plateforme doit offrir une expérience :

- simple ;
- rapide ;
- robuste ;
- fiable.

---

# 3. Personas concernés

Tous les personas utilisent WhatsApp.

- Coffi
- Aïcha
- Rodrigue
- Institutions
- Entrepreneur Agricole

---

# 4. Architecture

```
Utilisateur

↓

WhatsApp Cloud API

↓

Webhook

↓

Webhook Controller

↓

Event Router

↓

Media Processor

↓

NormalizedMessage

↓

Conversation Engine

↓

Reasoning Engine

↓

Response Builder

↓

WhatsApp Sender

↓

Utilisateur
```

---

# 5. Structure du module

```
integrations/

whatsapp/

controllers/

services/

events/

media/

templates/

security/

validators/

clients/

```

---

# 6. Responsabilités

La plateforme WhatsApp est responsable de :

- recevoir les événements ;
- vérifier les signatures ;
- télécharger les médias ;
- normaliser les messages ;
- transmettre les messages ;
- envoyer les réponses ;
- gérer les erreurs.

Elle ne réalise jamais de raisonnement.

---

# 7. Fonctionnalités

---

## FE-601 — Webhook Verification

Validation du webhook Meta.

Fonctions :

- vérification initiale
- validation des signatures
- sécurité

---

## FE-602 — Event Receiver

Réception des événements.

Exemples :

- message reçu
- message livré
- message lu
- erreur
- changement de statut

---

## FE-603 — Event Router

Identifier automatiquement :

- message texte
- audio
- image (V2)
- document (V2)

Puis transmettre au bon processeur.

---

## FE-604 — Media Downloader

Téléchargement sécurisé des médias.

Support V1 :

- audio

Prévu :

- image
- document
- vidéo

---

## FE-605 — Message Normalizer

Transformer un message WhatsApp en :

```
NormalizedMessage
```

Le reste du système ne dépend jamais du format WhatsApp.

---

## FE-606 — Response Sender

Envoyer :

- texte
- audio

Puis récupérer :

- identifiant du message
- statut d'envoi

---

## FE-607 — Error Manager

Gestion des erreurs.

Exemples :

- média indisponible
- webhook invalide
- API Meta indisponible
- utilisateur bloqué
- quota dépassé

---

## FE-608 — Retry Manager

Gestion automatique des nouvelles tentatives.

Objectifs :

- éviter les pertes de messages
- garantir la livraison

---

## FE-609 — Templates

Gestion des modèles WhatsApp.

Exemples :

- bienvenue
- reprise de conversation
- notifications
- messages système

---

# 8. User Stories

---

## US-601

En tant que Coffi,

je veux envoyer un message vocal,

afin de recevoir une réponse immédiatement.

---

## US-602

En tant qu'utilisateur,

je veux recevoir mes réponses directement dans WhatsApp.

---

## US-603

En tant qu'utilisateur,

je veux que mes conversations soient automatiquement reprises.

---

## US-604

En tant qu'administrateur,

je veux connaître les erreurs d'envoi,

afin de surveiller la plateforme.

---

# 9. Modèle conceptuel

```
Webhook Event

↓

Event Router

↓

Media Processor

↓

NormalizedMessage

↓

Conversation

↓

Reasoning

↓

Response

↓

WhatsApp Sender
```

---

# 10. Données manipulées

## Entrées

- texte
- audio

## Sorties

- texte
- audio

## Métadonnées

- numéro utilisateur
- identifiant Meta
- identifiant du message
- horodatage
- statut

---

# 11. Dépendances

Cette Epic dépend de :

- Conversation Engine
- Multimodal Engine
- Reasoning Engine

Elle utilise :

- WhatsApp Cloud API

---

# 12. Critères d'acceptation

Le système doit être capable de :

✓ recevoir un message WhatsApp

✓ vérifier le webhook

✓ télécharger un média

✓ normaliser les contenus

✓ créer ou reprendre une conversation

✓ transmettre la requête au moteur

✓ envoyer une réponse

✓ gérer les erreurs

✓ enregistrer les statuts des messages

---

# 13. Tests

## Tests unitaires

- Webhook Controller
- Event Router
- Downloader
- Sender
- Retry Manager

---

## Tests d'intégration

Utilisateur

↓

WhatsApp

↓

Webhook

↓

Conversation

↓

Reasoning

↓

Réponse

↓

WhatsApp

---

## Tests de charge

Simulation de milliers de messages simultanés.

---

# 14. Évolutions V2

- images
- vidéos
- documents
- réactions
- messages interactifs
- boutons
- listes
- localisation partagée
- appels API asynchrones
- notifications proactives

---

# 15. Définition de terminé

Cette Epic sera considérée comme terminée lorsque :

- un utilisateur pourra dialoguer avec SikaGlé exclusivement via WhatsApp ;
- les messages texte et audio seront pris en charge ;
- les conversations seront automatiquement reprises ;
- les réponses seront correctement délivrées ;
- les erreurs seront journalisées et gérées ;
- les tests fonctionnels et d'intégration seront validés.

---

# 16. Vision

La WhatsApp Platform est la porte d'entrée officielle de SikaGlé.

Elle masque toute la complexité technique du système et offre une expérience conversationnelle fluide aux agriculteurs.

Son rôle est de transformer chaque interaction WhatsApp en une requête standardisée pour le cœur de la plateforme, puis de restituer la réponse dans le format le plus adapté à l'utilisateur.

Elle constitue le premier point de contact entre SikaGlé et le terrain.


WhatsApp Cloud API
        │
        ▼
Webhook
        │
        ▼
Channel Gateway
        │
        ▼
Message Dispatcher
        │
        ▼
NormalizedMessage
        │
        ▼
Conversation Orchestrator
        │
        ├── Conversation Engine
        ├── Multimodal Engine
        ├── Agricultural Context Engine
        ├── Reasoning Engine
        ├── Knowledge Engine
        └── Response Builder
