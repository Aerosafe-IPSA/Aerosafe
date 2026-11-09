# Sprint 3 — Mise en place et conception (26 octobre → 1er novembre 2026)

## Planning (27 octobre 2026)

**Objectif du sprint** : tout le travail est suivi sur GitHub, le cahier des charges V3 est consolidé et la conception est posée.

| Story | Responsable | Points | Priorité |
|---|---|---|---|
| Créer l'organisation GitHub et le nouveau dépôt | Lucas | 1 | Must |
| Mise en place Scrum sur GitHub (docs, modèles, backlog, tableau) | Lucas, Tov | 3 | Must |
| Protection de `main` et règles de contribution | Tov | 1 | Must |
| Réimporter le script de test OpenSky dans le nouveau dépôt | Tov | 1 | Must |
| Cahier des charges V3 consolidé | Lucas | 5 | Must |
| Diagramme de classes et diagramme de séquence | Ryan | 3 | Must |
| Maquettes des écrans (connexion, recherche, fiche, dashboard) | Teddy | 3 | Must |
| Structure du projet et PostgreSQL sous Docker Compose | Tov | 3 | Must |

**Capacité engagée** : 20 points.

**Décision du 27 octobre** : le premier dépôt (compte personnel, privé) ne permettait pas de protéger `main` sans abonnement payant, ni de donner au Scrum Master les droits d'administration. L'équipe repart d'un dépôt public dans l'organisation GitHub `aerosafe-ipsa`. L'ancien dépôt est archivé et reste consultable comme trace du sprint 2.

## Daily

Voir la discussion GitHub « Daily – Sprint 3 ».

## Revue (9 novembre 2026)

> Revue tenue avec 8 jours de retard : le sprint n'a pas été clôturé le 1er novembre.

| Story | Responsable | Points | Terminée le | Trace |
|---|---|---|---|---|
| #7 Créer l'organisation GitHub et le nouveau dépôt | Lucas | 1 | 27 oct. | dépôt `aerosafe-ipsa/aerosafe` |
| #8 Mettre en place Scrum sur GitHub | Lucas, Tov | 3 | 27 oct. | PR #39, #40 |
| #9 Protéger la branche `main` | Tov, Lucas | 1 | 28 oct. | règles de protection de `main` |
| #10 Réimporter le script de test OpenSky | Tov | 1 | 29 oct. | PR #41 |
| #12 Diagramme de classes et diagramme de séquence | Ryan | 3 | 4 nov. | PR #42, #46 |
| #13 Maquettes des écrans | Teddy | 3 | 9 nov. | PR #43 |
| #11 Cahier des charges V3 | Lucas | 5 | 9 nov. | PR #48 |
| #14 Structure du projet et PostgreSQL sous Docker | Tov | 3 | 9 nov. | PR #44 |

Le diagramme de cas d'utilisation (#5, reporté du sprint 0) a aussi été livré par Ryan le 3 novembre (PR #45).

**Bilan** : les 20 points engagés sont livrés et acceptés par le Product Owner, mais seulement 6 l'étaient à la date de fin du sprint. Les 14 autres ont été terminés dans la semaine qui suivait.

**Version** : release `v0.3.0` (voir `CHANGELOG.md`).

## Rétrospective (9 novembre 2026)

**Ce qui a marché**
- Le travail est entièrement suivi sur GitHub : issues, milestones, tableau, branches et pull requests relues.
- La branche `main` est protégée : aucune fusion sans relecture depuis le 28 octobre.
- La conception est complète et cohérente : le diagramme de classes, le diagramme de séquence, les maquettes et le cahier des charges V3 utilisent les mêmes noms et les mêmes seuils.
- Les relectures ont servi : l'encapsulation a été décidée dans la PR #42, et la création du `.env` a été ajoutée au README dans la PR #44.

**Ce qui a bloqué**
- Le sprint a débordé de 8 jours : le sprint 4 démarre avec une semaine de retard, le 9 novembre.
- Des PR sont restées plusieurs jours sans relecture (#43 et #44 ont attendu une semaine).
- Le daily a été abandonné après le 29 octobre.
- Erreurs de forme : commits signés « Ton Nom » (configuration Git non faite), `closes(#12)` mal écrit (l'issue ne s'est pas fermée seule), descriptions de PR laissées vides.

**Actions pour la suite**
1. Toute PR est relue dans les 24 heures ; l'auteur désigne son relecteur à l'ouverture.
2. Daily écrit chaque jour dans la discussion du sprint ; Tov relance celui qui n'a rien posté.
3. Revue et rétrospective le dimanche, même si tout n'est pas terminé : ce qui n'est pas fini est reporté.
