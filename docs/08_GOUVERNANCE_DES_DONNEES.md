# 08_GOUVERNANCE_DES_DONNEES.md

# SikaGlé

## Gouvernance des Données

**Version :** 1.0

**Statut :** Officiel

**Dernière mise à jour :** Juillet 2026

---

# Préambule

Les données constituent l'un des actifs les plus précieux de SikaGlé.

Cependant, leur valeur ne doit jamais primer sur les droits des utilisateurs.

La gouvernance des données définit les règles qui encadrent la collecte, le stockage, l'utilisation, le partage et la suppression des données utilisées par SikaGlé.

Notre objectif est de garantir :

- la protection des utilisateurs ;
- la qualité des données ;
- la transparence ;
- la conformité réglementaire ;
- la confiance des partenaires.

---

# 1. Nos principes

Toutes les décisions concernant les données reposent sur cinq principes fondamentaux.

## Respect

Les utilisateurs restent propriétaires de leurs données personnelles.

---

## Transparence

Les utilisateurs doivent comprendre :

- quelles données sont collectées ;
- pourquoi elles sont collectées ;
- comment elles sont utilisées.

---

## Minimisation

Nous collectons uniquement les données nécessaires au fonctionnement du service.

Nous évitons toute collecte inutile.

---

## Sécurité

Toutes les données sont protégées contre :

- les accès non autorisés ;
- les pertes ;
- les modifications non souhaitées.

---

## Responsabilité

Chaque utilisation des données doit pouvoir être justifiée.

---

# 2. Catégories de données

Les données manipulées par SikaGlé sont classées en plusieurs catégories.

## Données personnelles

Exemples :

- numéro de téléphone ;
- nom (si fourni volontairement) ;
- langue préférée ;
- localisation approximative.

Ces données servent uniquement au fonctionnement du service.

---

## Données conversationnelles

Exemples :

- questions posées ;
- réponses générées ;
- messages vocaux ;
- images.

Ces données permettent :

- d'assurer le suivi des conversations ;
- d'améliorer les performances du système lorsque cela est autorisé.

---

## Données techniques

Exemples :

- journaux (logs) ;
- erreurs ;
- temps de réponse ;
- informations de diagnostic.

Ces données servent exclusivement à l'amélioration technique.

---

## Données documentaires

Il s'agit des connaissances utilisées par le moteur documentaire.

Exemples :

- publications scientifiques ;
- guides agricoles ;
- rapports techniques.

Ces données alimentent la base de connaissances.

---

## Observations agricoles anonymisées

Ce sont les données les plus stratégiques pour SikaGlé.

Exemple :

```json
{
  "culture": "manioc",
  "symptomes": [
    "feuilles jaunes"
  ],
  "commune": "Zogbodomey",
  "saison": "grande saison des pluies"
}
```

Ces observations ne permettent pas d'identifier un utilisateur.

---

# 3. Ce que nous ne collectons pas

SikaGlé ne collecte jamais volontairement :

- les mots de passe ;
- les données bancaires ;
- les conversations privées sans rapport avec le service ;
- les contacts téléphoniques ;
- les photos personnelles sans lien avec l'agriculture.

---

# 4. Finalités de la collecte

Chaque donnée collectée doit répondre à une finalité clairement identifiée.

Exemples :

- répondre à une question agricole ;
- personnaliser l'expérience utilisateur ;
- améliorer les performances du système ;
- produire des statistiques anonymisées.

Aucune donnée ne doit être collectée sans objectif légitime.

---

# 5. Utilisation des données

Les données sont utilisées uniquement pour :

- fournir un conseil agricole ;
- améliorer les diagnostics ;
- entraîner les modèles lorsque cela est autorisé ;
- produire des statistiques anonymisées ;
- assurer le fonctionnement du service.

---

# 6. Anonymisation

Toutes les observations utilisées pour les analyses sont anonymisées.

Les informations suivantes sont supprimées ou transformées :

- nom ;
- numéro de téléphone ;
- identifiants directs ;
- contenu permettant d'identifier une personne.

Les analyses portent uniquement sur les informations agricoles.

---

# 7. Partage des données

Les données personnelles ne sont jamais vendues.

Les partenaires peuvent uniquement accéder :

- à des données anonymisées ;
- à des statistiques agrégées ;
- à des indicateurs.

Aucun partenaire ne peut accéder aux conversations privées sans le consentement explicite de l'utilisateur ou sans obligation légale.

---

# 8. Qualité des données

Les données utilisées doivent être :

- exactes ;
- cohérentes ;
- à jour lorsque nécessaire ;
- vérifiables.

Les données erronées doivent être corrigées ou supprimées.

---

# 9. Sécurité

Les données sont protégées grâce à plusieurs mécanismes.

Exemples :

- authentification ;
- contrôle des accès ;
- chiffrement ;
- sauvegardes ;
- journalisation.

La sécurité doit être intégrée dès la conception ("Security by Design").

---

# 10. Durée de conservation

Les données ne sont conservées que pendant la durée nécessaire à leur finalité.

Les données personnelles peuvent être supprimées à la demande de l'utilisateur lorsque la réglementation le permet.

Les observations anonymisées peuvent être conservées plus longtemps à des fins statistiques et de recherche.

---

# 11. Droits des utilisateurs

Les utilisateurs disposent notamment des droits suivants :

- être informés ;
- accéder à leurs données ;
- demander la correction de données inexactes ;
- demander la suppression de leurs données lorsque cela est possible ;
- retirer leur consentement pour certaines utilisations.

---

# 12. Gouvernance interne

La gestion des données repose sur plusieurs responsabilités.

## Équipe Produit

Détermine les besoins fonctionnels.

---

## Équipe Technique

Met en œuvre les mécanismes de protection.

---

## Équipe IA

Garantit la qualité des modèles et des données d'entraînement.

---

## Direction du projet

Veille au respect des principes de gouvernance.

---

# 13. Éthique de l'intelligence artificielle

Les modèles d'IA utilisés par SikaGlé doivent respecter plusieurs principes.

- équité ;
- transparence ;
- explicabilité ;
- responsabilité ;
- robustesse.

Le système ne doit jamais produire volontairement de recommandations trompeuses.

Lorsque l'incertitude est importante, celle-ci doit être explicitement mentionnée.

---

# 14. Utilisation des observations anonymisées

Les observations anonymisées peuvent être utilisées pour :

- produire des statistiques ;
- détecter des tendances ;
- identifier des foyers de maladies ;
- améliorer les recommandations ;
- soutenir la recherche scientifique.

Ces utilisations doivent toujours préserver l'anonymat des producteurs.

---

# 15. Partenariats

Les partenaires de SikaGlé doivent respecter les mêmes exigences de protection des données.

Tout échange de données doit être encadré par un accord précisant :

- les données concernées ;
- leur finalité ;
- leur durée d'utilisation ;
- les responsabilités de chaque partie.

---

# 16. Audit

La gouvernance des données fera l'objet d'audits réguliers.

Les audits permettront notamment de vérifier :

- la conformité des traitements ;
- la qualité des données ;
- la sécurité ;
- le respect des principes éthiques.

---

# 17. Évolution

Cette politique est appelée à évoluer.

Toute modification devra :

- préserver les droits des utilisateurs ;
- renforcer la sécurité ;
- améliorer la transparence.

---

# Notre engagement

SikaGlé considère les données comme une responsabilité avant d'être une ressource.

Nous refusons toute utilisation des données qui serait contraire aux intérêts des producteurs.

Notre objectif est de construire une plateforme d'intelligence agricole fondée sur la confiance.

---

# Notre promesse

Les données personnelles des utilisateurs ne sont pas un produit.

La confiance des producteurs constitue le fondement même de SikaGlé.

Chaque décision relative aux données devra toujours respecter cette conviction.

---

# Conclusion

La gouvernance des données est un pilier essentiel de SikaGlé.

Elle garantit que les connaissances produites par la plateforme profitent à l'ensemble de l'écosystème agricole sans compromettre les droits individuels.

En protégeant les données personnelles tout en valorisant les observations anonymisées, SikaGlé construit une intelligence agricole collective, responsable et durable.
