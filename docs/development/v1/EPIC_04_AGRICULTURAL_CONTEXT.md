# EPIC_04_AGRICULTURAL_CONTEXT.md

# SikaGlé

# EPIC 04 — Agricultural Context

**Epic ID :** EPIC-04

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★☆

**Responsable :** Agricultural Context Engine

---

# 1. Objectif

Construire un moteur de contexte agricole capable d'enrichir automatiquement une demande utilisateur avec toutes les informations environnementales et agronomiques nécessaires.

Ce moteur fournit au Reasoning Engine un contexte complet afin d'améliorer la qualité des analyses et des recommandations.

Il ne prend aucune décision.

Il prépare les informations.

---

# 2. Valeur métier

Le même symptôme peut avoir plusieurs causes selon :

- la météo ;
- la saison ;
- la localisation ;
- le calendrier cultural ;
- les conditions climatiques récentes.

Le moteur de contexte permet donc d'éviter des recommandations génériques.

---

# 3. Personas concernés

Tous les personas.

Le contexte agricole améliore automatiquement les réponses fournies à :

- Coffi
- Aïcha
- Rodrigue
- Institutions
- Entrepreneurs Agricoles

---

# 4. Architecture

```

Conversation Engine

↓

Agricultural Context Engine

├── Location Service

├── Weather Service

├── Season Service

├── Crop Calendar Service

├── Agro-Ecological Zone Service

├── Soil Context Service (V2)

└── Regional Knowledge Service

↓

Reasoning Engine

```

---

# 5. Structure du module

```

agricultural_context/

models/

services/

providers/

weather/

location/

calendar/

regions/

season/

builders/

validators/

```

---

# 6. Responsabilités

Le moteur de contexte est responsable de :

- déterminer la localisation ;
- récupérer les données météo ;
- identifier la saison agricole ;
- déterminer le calendrier cultural ;
- identifier la zone agroécologique ;
- préparer un contexte structuré.

Il ne réalise aucun diagnostic.

---

# 7. Fonctionnalités

---

## FE-401 — Location Service

Déterminer la localisation de l'exploitation.

Sources possibles :

- profil utilisateur ;
- GPS ;
- commune ;
- département ;
- saisie manuelle.

---

## FE-402 — Weather Service

Récupération des données météorologiques.

Informations :

- température ;
- humidité ;
- pluie ;
- vent ;
- prévisions.

---

## FE-403 — Season Service

Détermination automatique :

- saison sèche ;
- saison des pluies ;
- période de transition.

---

## FE-404 — Crop Calendar Service

Déterminer le stade probable de la culture.

Exemple :

```
Culture : Maïs

↓

Date de semis

↓

Croissance

↓

Floraison

↓

Récolte
```

---

## FE-405 — Agro-Ecological Zone Service

Identifier automatiquement :

- zone agroécologique ;
- climat ;
- pratiques locales.

---

## FE-406 — Regional Knowledge Service

Associer des connaissances spécifiques à une région.

Exemples :

- maladies fréquentes ;
- ravageurs dominants ;
- cultures principales ;
- recommandations régionales.

---

## FE-407 — Context Builder

Fusionner toutes les informations dans un contexte unique.

Exemple :

```
{
location

weather

season

calendar

region

crop_stage

}
```

---

# 8. User Stories

---

## US-401

En tant que Coffi,

je veux que SikaGlé adapte ses conseils à la météo de ma commune.

---

## US-402

En tant qu'Aïcha,

je veux recevoir des recommandations correspondant à la période de culture actuelle.

---

## US-403

En tant que Rodrigue,

je veux que le système prenne en compte les spécificités régionales avant de proposer une solution.

---

## US-404

En tant qu'institution,

je veux que les recommandations soient cohérentes avec les réalités agroécologiques locales.

---

# 9. Modèle conceptuel

```

User

↓

Location

↓

Weather

↓

Season

↓

Crop Calendar

↓

Agro-Ecological Zone

↓

Agricultural Context

↓

Reasoning Engine

```

---

# 10. Données manipulées

## Localisation

- pays
- département
- commune
- coordonnées GPS

---

## Météo

- température
- humidité
- pluie
- vent
- prévisions

---

## Saison

- type de saison
- période agricole

---

## Calendrier cultural

- culture
- date de semis
- stade probable

---

## Zone agroécologique

- climat
- caractéristiques régionales

---

# 11. Dépendances

Cette Epic dépend :

- Conversation Engine
- User Profile
- Knowledge Platform

Elle fournit ses données au :

- Reasoning Engine

---

# 12. Critères d'acceptation

Le système doit être capable de :

✓ identifier la localisation

✓ récupérer la météo

✓ déterminer la saison

✓ déterminer le stade cultural

✓ identifier la zone agroécologique

✓ construire un contexte complet

✓ transmettre ce contexte au Reasoning Engine

---

# 13. Tests

## Tests unitaires

- Location Service
- Weather Service
- Season Service
- Calendar Service
- Context Builder

---

## Tests d'intégration

Conversation

↓

Localisation

↓

Météo

↓

Calendrier

↓

Context Builder

↓

Reasoning

---

## Tests métier

Comparer les recommandations générées avec celles attendues dans différents contextes agricoles (régions, saisons, cultures).

---

# 14. Évolutions V2

- contexte pédologique (type de sol) ;
- historique météorologique sur plusieurs semaines ;
- données satellitaires ;
- humidité des sols ;
- indices de végétation (NDVI) ;
- alertes phytosanitaires ;
- intégration avec des capteurs IoT.

---

# 15. Définition de terminé

Cette Epic sera terminée lorsque :

- la localisation sera déterminée automatiquement ou renseignée par l'utilisateur ;
- la météo sera intégrée dans les analyses ;
- la saison et le calendrier cultural seront correctement identifiés ;
- le contexte agricole sera transmis de manière structurée au Reasoning Engine ;
- tous les tests seront validés.

---

# 16. Vision

Le moteur de contexte agricole permet à SikaGlé de raisonner en tenant compte de la réalité du terrain.

Il transforme une question générique en une situation agricole contextualisée, intégrant l'environnement climatique, géographique et cultural.

Grâce à cette couche, les recommandations deviennent spécifiques, pertinentes et adaptées aux conditions réelles de production.


Agricultural Context Engine
│
├── User Context Provider
├── Location Context Provider
├── Weather Context Provider
├── Calendar Context Provider
├── AgroEcological Context Provider
├── Regional Knowledge Provider
└── Context Aggregator


