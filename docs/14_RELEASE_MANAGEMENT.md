# 14_RELEASE_MANAGEMENT.md

# SikaGlé

# Release Management

**Version :** 1.0

**Statut :** Officiel

---

# 1. Objectif

Définir le processus officiel de gestion des versions de SikaGlé.

Ce document décrit :

- la stratégie de versionnement ;
- le cycle de développement ;
- le processus de livraison ;
- les critères de validation ;
- la gestion des corrections ;
- la publication des nouvelles versions.

Il garantit que chaque version livrée est stable, documentée et reproductible.

---

# 2. Principes

Chaque version doit être :

- stable ;
- documentée ;
- testée ;
- traçable ;
- reproductible.

Aucune version ne peut être publiée sans respecter ces principes.

---

# 3. Cycle de vie d'une version

Chaque version suit le cycle suivant :

```
Backlog

↓

Analyse

↓

Développement

↓

Tests

↓

Release Candidate

↓

Validation

↓

Production

↓

Maintenance
```

---

# 4. Stratégie de versionnement

SikaGlé utilise le **Semantic Versioning (SemVer)**.

Format :

```
MAJOR.MINOR.PATCH
```

Exemple :

```
1.0.0
1.1.0
1.2.3
2.0.0
```

---

## MAJOR

Changement majeur.

Exemple :

- nouvelle architecture ;
- rupture de compatibilité.

---

## MINOR

Ajout de fonctionnalités compatibles.

Exemple :

- nouveau service ;
- nouvelle API ;
- nouvelle capacité.

---

## PATCH

Corrections.

Exemple :

- bug ;
- optimisation ;
- sécurité.

---

# 5. Versions de développement

Avant la V1 officielle :

```
0.1.0

0.2.0

0.3.0

...

0.9.0

1.0.0
```

Correspondance :

| Version | Epic |
|----------|------|
| 0.1 | Foundation |
| 0.2 | Knowledge Platform |
| 0.3 | Conversation |
| 0.4 | Reasoning |
| 0.5 | Agricultural Context |
| 0.6 | Multimodal |
| 0.7 | WhatsApp |
| 0.8 | API |
| 0.9 | Production Candidate |
| 1.0 | Première version publique |

---

# 6. Branches Git

Le projet utilise une stratégie Git simple.

```
main

↓

release

↓

feature/*
```

## main

Toujours stable.

Correspond à la production.

---

## release

Préparation de la prochaine version.

---

## feature/*

Développement d'une fonctionnalité.

Exemple :

```
feature/conversation-memory

feature/reasoning-engine

feature/weather-context
```

---

# 7. Développement

Chaque fonctionnalité suit le processus suivant.

```
Epic

↓

Feature

↓

User Story

↓

Task

↓

Code

↓

Tests

↓

Merge

↓

Release
```

---

# 8. Critères d'entrée en Release

Une fonctionnalité peut intégrer une Release uniquement si :

✓ développement terminé

✓ revue de code validée

✓ tests unitaires validés

✓ tests d'intégration validés

✓ documentation mise à jour

✓ critères d'acceptation validés

---

# 9. Release Candidate

Avant chaque version officielle :

```
Version

↓

Release Candidate

↓

Validation

↓

Production
```

Exemple :

```
1.0.0-rc1

1.0.0-rc2

1.0.0
```

---

# 10. Validation

Une Release Candidate est validée si :

- aucune régression critique ;
- aucun bug bloquant ;
- performances conformes ;
- documentation complète ;
- validation fonctionnelle.

---

# 11. Déploiement

Le déploiement suit les étapes suivantes.

```
Développement

↓

Tests

↓

Release Candidate

↓

Production

↓

Surveillance
```

Le déploiement doit être automatisé.

---

# 12. Rollback

Chaque version doit pouvoir être annulée.

En cas d'incident :

```
Nouvelle version

↓

Erreur

↓

Rollback

↓

Version précédente
```

Le rollback doit être documenté et testé.

---

# 13. Hotfix

En cas de bug critique.

```
Production

↓

Hotfix

↓

Tests

↓

Déploiement
```

Exemple :

```
1.0.1

1.0.2
```

---

# 14. Changelog

Chaque version possède un changelog.

Format recommandé :

## Ajouts

## Améliorations

## Corrections

## Sécurité

## Dépréciations

## Ruptures de compatibilité

---

# 15. Documentation

Avant chaque release :

- API à jour ;
- documentation utilisateur à jour ;
- documentation technique à jour ;
- guides d'exploitation à jour.

---

# 16. Qualité

Avant publication :

✓ tous les tests passent

✓ couverture minimale respectée

✓ sécurité validée

✓ performances validées

✓ monitoring opérationnel

✓ sauvegardes vérifiées

---

# 17. Suivi après déploiement

Pendant les premières heures suivant une release :

surveiller :

- erreurs ;
- disponibilité ;
- consommation mémoire ;
- temps de réponse ;
- appels LLM ;
- appels WhatsApp.

---

# 18. Dépréciation

Une fonctionnalité ne peut être supprimée que si :

- elle est documentée comme obsolète ;
- une alternative existe ;
- les utilisateurs ont été informés.

---

# 19. Rôles

## Product Owner

- valide les fonctionnalités ;
- décide des priorités.

---

## Développeur

- implémente ;
- teste ;
- documente.

---

## Relecteur

- valide la qualité du code ;
- vérifie les standards.

---

## Responsable Release

- prépare la version ;
- valide le déploiement ;
- supervise la mise en production.

---

# 20. Checklist de Release

## Produit

- [ ] Toutes les User Stories prévues sont terminées
- [ ] Critères d'acceptation validés
- [ ] Documentation mise à jour

## Technique

- [ ] Build réussi
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests fonctionnels
- [ ] Tests de performance

## Production

- [ ] Variables d'environnement vérifiées
- [ ] Sauvegardes réalisées
- [ ] Monitoring actif
- [ ] Alertes configurées

## Communication

- [ ] Changelog rédigé
- [ ] Numéro de version attribué
- [ ] Release publiée

---

# 21. Historique des versions

| Version | Date | Statut | Description |
|----------|------|--------|-------------|
| 0.1.0 | À compléter | Foundation | Architecture initiale |
| 0.2.0 | À compléter | Knowledge | Plateforme documentaire |
| 0.3.0 | À compléter | Prévue | Conversation Engine |
| 0.4.0 | À compléter | Prévue | Reasoning Engine |
| 0.5.0 | À compléter | Prévue | Agricultural Context |
| 0.6.0 | À compléter | Prévue | Multimodal |
| 0.7.0 | À compléter | Prévue | WhatsApp |
| 0.8.0 | À compléter | Prévue | API |
| 0.9.0 | À compléter | Prévue | Production Candidate |
| 1.0.0 | À compléter | Prévue | Première version publique |

---

# 22. Vision

La gestion des releases garantit que SikaGlé évolue de manière progressive, maîtrisée et fiable.

Chaque version représente une amélioration mesurable du produit, validée sur les plans fonctionnel, technique et métier.

L'objectif n'est pas de livrer rapidement, mais de livrer un assistant agricole fiable, maintenable et capable d'évoluer durablement au service des producteurs, des agronomes et des institutions.
