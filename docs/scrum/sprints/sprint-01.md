# Sprint 1 — Organisation et données (28 septembre → 11 octobre 2026)

> Compte rendu **rédigé a posteriori** le 27 octobre 2026, à partir du travail réellement effectué.

## Objectif du sprint

Se répartir le travail et identifier la source de données.

## Réalisé

| Élément | Responsable | Date |
|---|---|---|
| Répartition des tâches, Lucas prend en charge la collecte des données | Équipe | 1er oct. 2026 |
| Étude de l'API OpenSky (OAuth2, quotas de crédits, champs utiles aux règles R1 à R5) | Lucas | 1er oct. 2026 |

## Revue

L'API OpenSky répond aux besoins : chaque règle R1 à R5 s'appuie sur un champ précis (dernier contact, horodatage de position, altitude, vitesse, cap). Les règles R3 à R5 comparant deux observations, il faudra stocker l'historique et pas seulement la dernière position.

## Rétrospective

- **Ce qui a marché** : la source de données est identifiée et ses limites connues (quotas, authentification).
- **Ce qui bloque** : pas d'endroit unique pour suivre le travail et partager le code.
- **Action pour S2** : créer un dépôt Git commun.
