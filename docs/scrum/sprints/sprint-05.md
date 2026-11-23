# Sprint 5 — Règles, alertes et API (9 → 15 novembre 2026)

> Compte rendu rédigé par le Product Owner le 23 novembre 2026, à partir de l'état du dépôt. Ce sprint a chevauché le sprint 4, démarré avec une semaine de retard ; il n'a pas eu de planning ni de daily propres.

## Contenu prévu

**Objectif du sprint** : les règles R1 à R5 produisent des alertes enregistrées en base, et l'API permet de rechercher un aéronef et de tracer son trajet.

| Story | Responsable | Points | Priorité |
|---|---|---|---|
| #21 Règles R3, R4 et R5 | Ryan | 3 | Must |
| #22 Enregistrer les alertes | Ryan | 3 | Must |
| #23 API : rechercher un avion | Lucas | 3 | Must |
| #24 API : trajet d'un avion | Lucas | 2 | Must |
| #27 Page d'un avion avec la carte | Teddy | 5 | Must |
| #17 Données de secours pour la démo | Tov | 2 | Must |
| #31 Tout lancer avec docker compose up | Tov | 3 | Must |

**Capacité prévue** : 21 points.

## Revue (23 novembre 2026)

| Story | État | Trace |
|---|---|---|
| #23 API : rechercher un avion | Livrée le 20 nov. | PR #60 |
| #24 API : trajet d'un avion | Livrée le 20 nov. | PR #60 |
| #21, #22, #27, #17, #31 | Non commencées | — |

**Bilan** : 0 point livré à la date de fin, 5 points sur 21 au 20 novembre. Les cinq stories restantes, toutes Must, sont reportées au sprint 7.

L'API répond en moins de 40 ms sur une base de 108 000 positions (exigence BNF-01 : moins de 2 secondes). La PR #60 a été fusionnée dans la branche de #16 avant d'arriver dans `main` avec la PR #59 : les issues #23 et #24 ont donc été fermées à la main.

## Rétrospective (23 novembre 2026)

**Ce qui a marché**

- La base (#16) et l'API (#23, #24) ont été livrées le même jour, chacune dans sa PR, avec 37 tests au total.

**Ce qui a bloqué**

- Le sprint n'a pas existé en pratique : toute l'équipe terminait encore le sprint 4.
- Cinq stories sur sept n'ont pas été commencées, dont le cœur du sujet : les règles R3 à R5 et l'enregistrement des alertes.

**Action**

1. Ne plus engager un sprint tant que le précédent n'est pas clos par une revue.
