# 03_ARCHITECTURE_FONCTIONNELLE.md

# SikaGlé

## Architecture Fonctionnelle

**Version :** 1.0

**Statut :** Officiel

**Dernière mise à jour :** Juillet 2026

---

# 1. Objectif du document

Ce document décrit l'architecture fonctionnelle de SikaGlé.

Il présente les différents composants du système, leurs responsabilités et leurs interactions.

Contrairement à l'architecture technique, ce document ne décrit pas les technologies utilisées (FastAPI, Python, ChromaDB, etc.), mais explique **comment le produit fonctionne** du point de vue métier.

Il constitue la référence pour tous les développements futurs.

---

# 2. Vue d'ensemble

SikaGlé est une plateforme d'intelligence artificielle spécialisée dans le conseil agricole.

Son fonctionnement repose sur une chaîne de traitement capable de :

- comprendre l'utilisateur ;
- comprendre son problème ;
- rechercher les connaissances utiles ;
- raisonner ;
- produire une réponse adaptée.

L'architecture est conçue sous forme de modules indépendants pouvant évoluer sans remettre en cause le fonctionnement global.

---

# 3. Vue globale de l'architecture

```text
                                      SikaGlé

                                            │

      ┌─────────────────────────────────────┼─────────────────────────────────────┐

      │                                     │                                     │

 Interface Utilisateur              Moteur d'Intelligence                 Services Métier

      │                                     │                                     │

 WhatsApp                        Compréhension IA                     Gestion documentaire

 Web                             Raisonnement                         Météo

 API                             Recherche                            Analytics

 Mobile (future)                 Génération                           Dashboard
```

---

# 4. Les grands domaines fonctionnels

L'architecture de SikaGlé est organisée autour de six grands domaines.

## 1. Interfaces utilisateur

Responsabilité :

Recevoir les demandes des utilisateurs et transmettre les réponses.

Canaux prévus :

- WhatsApp
- Application Web
- Application Mobile (future)
- API

Entrées possibles :

- Texte
- Audio
- Images

Sorties possibles :

- Texte
- Audio
- Images annotées
- Documents PDF

---

## 2. Compréhension des demandes

Ce domaine transforme une demande brute en informations exploitables.

Exemple :

Message vocal :

> Mes feuilles deviennent jaunes.

Le système identifie :

- langue ;
- culture ;
- symptômes ;
- contexte ;
- intention.

Modules concernés :

- Speech-to-Text
- Détection de langue
- Analyse linguistique
- Extraction d'informations

Sortie :

Un cas agricole structuré.

---

## 3. Moteur de raisonnement

Le moteur de raisonnement constitue le cerveau de SikaGlé.

Son rôle est de comprendre le problème agricole.

Il ne répond jamais directement.

Il commence par analyser :

- la culture concernée ;
- les symptômes ;
- les traitements déjà appliqués ;
- la météo ;
- la saison ;
- les informations manquantes.

Puis il élabore plusieurs hypothèses.

Enfin il décide :

- quelles informations rechercher ;
- quelles questions complémentaires poser ;
- comment construire la réponse.

---

# 5. Recherche documentaire (RAG)

Le moteur documentaire permet à SikaGlé de consulter sa base de connaissances.

Les connaissances proviennent notamment de :

- publications scientifiques ;
- guides techniques ;
- rapports de recherche ;
- documents institutionnels.

Le moteur effectue :

- recherche vectorielle ;
- recherche par mots-clés ;
- recherche hybride ;
- réordonnancement des résultats.

Les documents retrouvés servent de base à la génération des réponses.

---

# 6. Services contextuels

Pour améliorer la pertinence des réponses, plusieurs services peuvent être consultés.

Exemples :

- météo ;
- calendrier agricole ;
- géolocalisation ;
- historique utilisateur ;
- mémoire de l'exploitation.

Ces informations permettent d'adapter les recommandations au contexte réel.

---

# 7. Génération des réponses

Une fois le raisonnement terminé, le système construit la réponse.

Les réponses peuvent prendre plusieurs formes.

Texte.

Audio.

Image annotée.

Rapport PDF.

Le contenu doit toujours être :

- clair ;
- compréhensible ;
- contextualisé ;
- justifié lorsque possible.

---

# 8. Gestion des connaissances

Les connaissances constituent le patrimoine principal de SikaGlé.

Elles sont :

- collectées ;
- nettoyées ;
- découpées ;
- vectorisées ;
- indexées.

Elles alimentent ensuite le moteur documentaire.

Les nouvelles publications pourront être ajoutées sans modifier le fonctionnement du reste du système.

---

# 9. Observations agricoles

Chaque interaction utilisateur peut produire une observation.

Exemple :

- culture
- symptômes
- commune
- langue
- saison

Les observations sont anonymisées avant toute exploitation.

Elles serviront à produire :

- statistiques ;
- alertes ;
- indicateurs ;
- prévisions.

---

# 10. Tableau de bord institutionnel

Les données anonymisées pourront alimenter des tableaux de bord.

Exemples :

- évolution des maladies ;
- cartes des ravageurs ;
- répartition géographique ;
- tendances saisonnières ;
- indicateurs agricoles.

Ces tableaux de bord sont destinés aux institutions partenaires.

---

# 11. API

Toutes les fonctionnalités de SikaGlé devront pouvoir être utilisées via des API.

Exemples :

- diagnostic agricole ;
- recherche documentaire ;
- météo ;
- traduction ;
- statistiques.

Cette approche permettra à des applications tierces de réutiliser les services de SikaGlé.

---

# 12. Flux fonctionnel général

Le fonctionnement global de SikaGlé suit le processus suivant.

```text
Utilisateur

↓

Texte / Audio / Image

↓

Compréhension

↓

Détection de langue

↓

Extraction des informations

↓

Construction du cas agricole

↓

Moteur de raisonnement

↓

Recherche documentaire

↓

Services contextuels

↓

Fusion des connaissances

↓

Génération de la réponse

↓

Texte / Audio

↓

Utilisateur
```

---

# 13. Flux détaillé

## Étape 1

L'utilisateur formule sa demande.

---

## Étape 2

Le système identifie :

- la langue ;
- le type de demande ;
- les informations disponibles.

---

## Étape 3

Les informations importantes sont extraites.

Exemple :

Culture :

Manioc.

Symptôme :

Feuilles jaunes.

Contexte :

Pluie récente.

---

## Étape 4

Le moteur de raisonnement construit plusieurs hypothèses.

---

## Étape 5

Le moteur documentaire recherche les connaissances pertinentes.

---

## Étape 6

Les services contextuels complètent l'analyse.

---

## Étape 7

Le modèle d'IA construit une réponse.

---

## Étape 8

La réponse est adaptée au canal utilisé.

Texte.

Ou audio.

---

# 14. Principes architecturaux

L'architecture de SikaGlé repose sur plusieurs principes.

## Modularité

Chaque module est indépendant.

---

## Évolutivité

Un nouveau service peut être ajouté sans modifier les autres.

---

## Réutilisabilité

Chaque module peut être utilisé séparément.

---

## Robustesse

Une erreur dans un service ne doit pas provoquer l'arrêt complet du système.

---

## Observabilité

Chaque étape importante doit pouvoir être journalisée afin de faciliter les analyses et le débogage.

---

# 15. Les principaux modules

L'architecture fonctionnelle comprend les modules suivants.

- Interfaces utilisateur
- Gestion des conversations
- Compréhension du langage
- Reconnaissance vocale
- Traduction
- Détection de langue
- Analyse des images
- Moteur de raisonnement
- Recherche documentaire
- Gestion des connaissances
- Services météo
- Génération des réponses
- Synthèse vocale
- Analytics
- Tableau de bord
- API publique

---

# 16. Les principes de fonctionnement

SikaGlé applique toujours les règles suivantes.

Comprendre avant de répondre.

Raisonner avant de conclure.

Rechercher avant d'affirmer.

Contextualiser avant de recommander.

Expliquer avant de conseiller.

Citer ses sources lorsque cela est possible.

---

# 17. Vision d'évolution

Cette architecture est conçue pour évoluer progressivement.

Version 1

Assistant WhatsApp intelligent.

Version 2

Assistant multimodal.

Version 3

Plateforme agricole.

Version 4

Infrastructure agricole régionale.

---

# Conclusion

L'architecture fonctionnelle de SikaGlé a été pensée pour séparer clairement les responsabilités de chaque domaine tout en permettant leur collaboration.

Cette approche garantit :

- une meilleure maintenabilité ;
- une évolution progressive ;
- une intégration facilitée de nouveaux services ;
- une meilleure qualité des réponses fournies aux utilisateurs.

Cette architecture constitue la référence fonctionnelle de l'ensemble du projet et guidera toutes les décisions techniques futures.
