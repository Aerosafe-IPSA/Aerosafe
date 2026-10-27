# Notre méthode Scrum

## Calendrier des sprints

Pendant la phase de cadrage, nous avons travaillé en sprints de **deux semaines**. À partir du sprint 3, nous passons à des sprints d'**une semaine** : l'approche du rendu (1er décembre) demande des points de contrôle plus fréquents (décision prise le 27 octobre, lors de la mise en place de la méthode sur GitHub).

| Sprint | Dates | Objectif |
|---|---|---|
| S0 | 14 → 27 sept. 2026 | Cadrage, cahiers des charges V1 et V2 |
| S1 | 28 sept. → 11 oct. 2026 | Organisation et étude des données OpenSky |
| S2 | 12 → 25 oct. 2026 | Premier dépôt Git, premier accès à l'API OpenSky |
| S3 | 26 oct. → 1er nov. 2026 | Mise en place Scrum/GitHub, cahier des charges V3, conception |
| S4 | 2 → 8 nov. 2026 | Collecteur OpenSky, base de données, authentification |
| S5 | 9 → 15 nov. 2026 | Moteur de règles et API, tests |
| S6 | 16 → 22 nov. 2026 | Interface web, intégration continue |
| S7 | 23 → 29 nov. 2026 | Finitions, documentation, release v1.0 |
| S8 | 30 nov. → 6 déc. 2026 | Présentation, répétitions de la démo, module IA (bonus) |

Jalons fixes : **1er décembre** envoi du cahier des charges et du lien GitHub — **9 décembre à 14h** soutenance.

## Cérémonies

| Cérémonie | Quand | Durée | Trace laissée |
|---|---|---|---|
| Sprint planning | Lundi, début de sprint | 30 min | `docs/scrum/sprints/sprint-XX.md` (partie Planning) + issues assignées au milestone |
| Daily | Lun. à ven., asynchrone | 2 min par personne | Commentaire dans la discussion GitHub « Daily – Sprint X » : *hier / aujourd'hui / blocage* |
| Sprint review | Dimanche, fin de sprint | 20 min | Partie Revue du compte rendu, stories acceptées ou refusées par le PO |
| Rétrospective | Juste après la revue | 15 min | Partie Rétro : ce qui marche, ce qui bloque, une action pour le sprint suivant |

## Outils

- **Dépôt** : organisation GitHub `aerosafe-ipsa`, dépôt public, branche `main` protégée.
- **Backlog et tableau** : GitHub Projects, colonnes *Backlog → Sprint → En cours → En revue → Terminé*.
- **User stories** : issues GitHub créées avec le modèle « User story » (points, priorité MoSCoW, critères d'acceptation).
- **Sprints** : un milestone GitHub par sprint.
- **Code** : une branche et une pull request par story (voir `CONTRIBUTING.md`).
- **Versions** : un tag et une release GitHub en fin de sprint dès que du code est livré (voir `CHANGELOG.md`).

## Estimation et priorisation

- Points de complexité sur la suite 1, 2, 3, 5, 8. Une story à 8 doit être découpée.
- Priorité **MoSCoW** : *Must* (indispensable au MVP), *Should* (attendu, reportable d'un sprint), *Could* (bonus, ex. module IA), *Won't* (hors périmètre).
- Si le sprint déborde, ce sont les *Could* puis les *Should* qui glissent, jamais la date.

## Définition du « terminé » (Definition of Done)

Une story n'est terminée que si **tous** les points suivants sont vrais :

1. Le code est sur une branche dédiée et fusionné dans `main` via une pull request.
2. La PR est liée à son issue (`Closes #N`) et a été relue et approuvée par au moins un autre membre.
3. Les vérifications automatiques (CI) passent, dès qu'elles sont en place.
4. La logique métier est couverte par des tests unitaires.
5. Les classes et fonctions publiques ont une docstring.
6. Les critères d'acceptation de l'issue sont vérifiés par le Product Owner.
