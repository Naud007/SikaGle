# 09_DECISIONS_ARCHITECTURALES.md

# SikaGlé

## Journal des Décisions Architecturales (ADR)

**Version :** 1.0

**Statut :** Officiel

**Dernière mise à jour :** Juillet 2026

---

# Préambule

Ce document consigne les décisions architecturales majeures prises au cours du développement de SikaGlé.

Chaque décision est documentée afin de conserver son contexte, les alternatives étudiées, les raisons du choix retenu et les conséquences pour le projet.

Les ADR (Architecture Decision Records) constituent la mémoire technique du projet.

Ils permettent de comprendre les choix passés, d'éviter les débats récurrents et de faciliter l'intégration de nouveaux développeurs.

---

# Format des ADR

Chaque décision suit le format suivant :

- Identifiant
- Date
- Statut
- Contexte
- Alternatives étudiées
- Décision retenue
- Justification
- Conséquences

---

# ADR-001 — Architecture modulaire

## Statut

Acceptée

---

## Contexte

SikaGlé est destiné à évoluer progressivement, avec de nombreux modules (RAG, météo, vision, analytics, dashboard, etc.).

Une architecture monolithique aurait rapidement rendu le projet difficile à maintenir.

---

## Alternatives

- Monolithe classique
- Architecture orientée services
- Architecture modulaire

---

## Décision

Adopter une architecture modulaire organisée par domaines métier.

---

## Justification

Cette architecture :

- simplifie la maintenance ;
- facilite les tests ;
- permet l'évolution progressive du système ;
- favorise la réutilisation des composants.

---

## Conséquences

Chaque domaine métier possède son propre module avec une responsabilité clairement définie.

---

# ADR-002 — FastAPI comme framework principal

## Statut

Acceptée

---

## Contexte

Le backend de SikaGlé doit fournir une API performante, documentée et facilement extensible.

---

## Alternatives

- Django
- Flask
- FastAPI

---

## Décision

Utiliser FastAPI.

---

## Justification

FastAPI offre :

- d'excellentes performances ;
- une documentation OpenAPI automatique ;
- une validation forte des données grâce à Pydantic ;
- un excellent support de l'asynchrone.

---

## Conséquences

L'ensemble des services backend est développé autour de FastAPI.

---

# ADR-003 — Utilisation du RAG

## Statut

Acceptée

---

## Contexte

Les modèles de langage ne disposent pas toujours de connaissances agricoles précises ou à jour.

---

## Alternatives

- LLM seul
- Base de connaissances classique
- Retrieval-Augmented Generation (RAG)

---

## Décision

Utiliser une architecture RAG.

---

## Justification

Le RAG permet :

- d'utiliser des documents scientifiques récents ;
- de citer les sources ;
- de réduire les hallucinations ;
- de mettre à jour les connaissances sans réentraîner le modèle.

---

## Conséquences

Le Knowledge Engine devient un composant central de SikaGlé.

---

# ADR-004 — Recherche hybride

## Statut

Acceptée

---

## Contexte

La recherche vectorielle est performante pour les requêtes sémantiques, mais moins efficace pour certains termes techniques ou noms spécifiques.

---

## Alternatives

- Recherche vectorielle uniquement
- Recherche par mots-clés uniquement
- Recherche hybride

---

## Décision

Combiner la recherche vectorielle et la recherche par mots-clés.

---

## Justification

Cette approche améliore :

- la pertinence ;
- le rappel ;
- la robustesse des résultats.

---

## Conséquences

Le moteur de recherche combine plusieurs scores avant de classer les documents.

---

# ADR-005 — Moteur de raisonnement distinct du LLM

## Statut

Acceptée

---

## Contexte

Un LLM répond directement à une question, mais ne suit pas toujours un raisonnement structuré.

---

## Alternatives

- Laisser le LLM répondre directement
- Ajouter un moteur de raisonnement dédié

---

## Décision

Créer un Reasoning Engine indépendant.

---

## Justification

Le moteur de raisonnement :

- identifie les informations manquantes ;
- construit des hypothèses ;
- prépare les requêtes vers la base documentaire ;
- améliore la qualité des réponses.

---

## Conséquences

Le LLM devient un composant d'exécution, tandis que le raisonnement reste contrôlé par SikaGlé.

---

# ADR-006 — Séparation entre connaissances et observations

## Statut

Acceptée

---

## Contexte

Les publications scientifiques et les observations terrain n'ont pas le même rôle.

---

## Alternatives

- Stocker toutes les données dans une même base
- Séparer les flux de données

---

## Décision

Maintenir deux flux indépendants :

- base documentaire ;
- observations agricoles anonymisées.

---

## Justification

Cette séparation :

- améliore la qualité des connaissances ;
- protège les données personnelles ;
- facilite les analyses statistiques.

---

## Conséquences

Les observations anonymisées alimentent les tableaux de bord sans modifier directement la base documentaire.

---

# ADR-007 — WhatsApp comme premier canal

## Statut

Acceptée

---

## Contexte

Les producteurs agricoles disposent majoritairement d'un téléphone mobile avec WhatsApp.

---

## Alternatives

- Application mobile native
- Site web
- WhatsApp

---

## Décision

Commencer par WhatsApp.

---

## Justification

WhatsApp :

- est déjà largement adopté ;
- ne nécessite pas d'installation supplémentaire ;
- prend en charge le texte, l'audio, les images et les documents.

---

## Conséquences

Les interfaces web et mobiles seront développées dans un second temps.

---

# ADR-008 — Architecture multimodale

## Statut

Acceptée

---

## Contexte

Les producteurs utilisent différents moyens pour communiquer.

---

## Décision

Concevoir SikaGlé dès le départ comme un système multimodal.

---

## Entrées

- texte ;
- audio ;
- image.

---

## Sorties

- texte ;
- audio.

---

## Justification

Cette approche garantit une meilleure accessibilité et prépare les évolutions futures.

---

# ADR-009 — Personnalisation par personas

## Statut

Acceptée

---

## Contexte

Les utilisateurs ont des besoins très différents.

---

## Décision

Construire le produit autour de cinq personas officiels.

---

## Justification

Les réponses, le niveau de détail et les interfaces peuvent être adaptés au profil de chaque utilisateur.

---

## Conséquences

Toute nouvelle fonctionnalité doit identifier le ou les personas concernés.

---

# ADR-010 — Intelligence collective fondée sur l'anonymisation

## Statut

Acceptée

---

## Contexte

Les observations terrain peuvent améliorer les recommandations et les analyses.

---

## Décision

N'utiliser que des observations anonymisées pour produire des statistiques et des tableaux de bord.

---

## Justification

Cette approche protège la vie privée tout en créant une intelligence collective utile aux producteurs, aux chercheurs et aux institutions.

---

## Conséquences

Les données personnelles ne sont jamais exploitées à des fins statistiques.

---

# Gestion des nouvelles décisions

Toute décision architecturale importante devra être ajoutée à ce document.

Chaque ADR reçoit un identifiant unique :

- ADR-011
- ADR-012
- ADR-013
- ...

Les anciennes décisions ne sont jamais supprimées.

Si une décision évolue, un nouvel ADR est créé pour documenter le changement.

---

# Révision des ADR

Les ADR sont révisés :

- lors des changements majeurs d'architecture ;
- avant chaque version majeure du produit ;
- lorsqu'une décision est remise en question.

L'historique des décisions est conservé afin d'assurer la traçabilité du projet.

---

# Conclusion

Les décisions architecturales représentent la mémoire technique de SikaGlé.

En documentant systématiquement les choix structurants, le projet garantit la cohérence de son évolution, facilite la collaboration entre les développeurs et préserve les raisons qui ont guidé sa conception.

Ce document accompagnera SikaGlé tout au long de son développement et constituera une référence pour chaque évolution majeure de la plateforme.
