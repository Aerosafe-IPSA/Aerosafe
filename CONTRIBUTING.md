# Contribuer à AeroSafe

## Principe

On ne pousse **jamais** directement sur `main` (la branche est protégée). Chaque story du backlog suit le même chemin :

```
issue → branche → commits → pull request → relecture → fusion dans main → issue fermée
```

## 1. Créer la branche

Partir de `main` à jour, et nommer la branche avec le numéro de l'issue :

```bash
git switch main
git pull
git switch -c feature/12-moteur-regles
```

Préfixes : `feature/` (fonctionnalité), `fix/` (correction), `docs/` (documentation), `chore/` (configuration, outillage).

## 2. Committer

Messages au format *Conventional Commits*, en français :

```
feat(regles): ajoute la règle R5 de changement de cap
fix(collecte): ignore les états sans position
docs(scrum): compte rendu du sprint 4
test(regles): cas du passage 350° → 10° pour R5
chore(ci): ajoute ruff au workflow
```

Des petits commits fréquents valent mieux qu'un gros commit en fin de sprint.

## 3. Ouvrir la pull request

```bash
git push -u origin feature/12-moteur-regles
```

Sur GitHub, ouvrir la PR vers `main`, remplir le modèle et écrire `Closes #12` pour que l'issue se ferme automatiquement à la fusion.

## 4. Relecture

- Au moins **une approbation** d'un autre membre est nécessaire, en priorité le référent du domaine (voir `docs/scrum/equipe.md`).
- Le relecteur commente dans la PR ; les corrections se font par de nouveaux commits sur la même branche.
- Une fois approuvée, l'auteur fusionne la PR et supprime la branche.

## 5. Versions

En fin de sprint, si du code a été livré, le Scrum Master crée un tag et une release GitHub (`v0.3.0`, `v0.4.0`, … `v1.0.0`) et met à jour `CHANGELOG.md`.

## Style de code

- Python 3.11, norme PEP 8.
- Programmation orientée objet pour la logique métier (collecteur, règles, services).
- Docstrings au format Google sur chaque classe et fonction publique.
