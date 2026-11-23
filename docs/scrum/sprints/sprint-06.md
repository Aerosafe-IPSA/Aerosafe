# Sprint 6 — Interface et finitions (16 → 22 novembre 2026)

> Compte rendu rédigé par le Product Owner le 23 novembre 2026, à partir de l'état du dépôt. Ce sprint n'a pas eu de planning ni de daily : la semaine a servi à livrer les stories en retard des sprints 4 et 5.

## Contenu prévu

**Objectif du sprint** : le superviseur dispose de son dashboard, et la version 1.0 est prête.

| Story | Responsable | Points | Priorité |
|---|---|---|---|
| #28 Dashboard superviseur | Teddy | 5 | Must |
| #33 Version 1.0 et rendu du 1er décembre | Lucas | 1 | Must |
| #29 Modifier les seuils des règles | Ryan | 3 | Should |
| #30 Filtrer et traiter les alertes | Ryan | 3 | Should |
| #32 Documentation du code en ligne | Tov | 2 | Should |

**Capacité prévue** : 14 points.

## Revue (23 novembre 2026)

| Story | État | Trace |
|---|---|---|
| #28 Dashboard superviseur | En relecture | PR #62, ouverte le 20 nov. |
| #33, #29, #30, #32 | Non commencées | — |

**Bilan** : 0 point livré sur 14. Pendant cette semaine, l'équipe a livré 13 points des sprints précédents le 20 novembre (#16, #20, #23, #24).

**Réserve du Product Owner sur la PR #62** : le dashboard affiche des chiffres et des alertes écrits dans la page, sans lien avec l'API ni avec les règles R1 à R5. Il ne pourra être accepté qu'une fois branché sur les données réelles, ce qui dépend de #22.

## Rétrospective (23 novembre 2026)

**Ce qui a marché**

- La journée du 20 novembre : quatre stories livrées, relues et fusionnées.

**Ce qui a bloqué**

- L'interface avance sans les données : les pages sont écrites avant les routes de l'API dont elles ont besoin, puis doivent être refaites.
- Le retard cumulé des sprints 4 et 5 a occupé toute la semaine.

**Action**

1. Pour chaque page restante, la route de l'API est livrée avant la page, ou les deux dans la même semaine par deux personnes qui se coordonnent.
