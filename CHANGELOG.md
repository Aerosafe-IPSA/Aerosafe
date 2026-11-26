# Journal des versions

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Une version par sprint ayant livré du code.

## [v0.4.0] — 23 novembre 2026 — Sprints 4 et 5

### Ajouté
- Collecte OpenSky toutes les 60 secondes (`python -m collector`) : classe `CollecteurOpenSky`, accès OAuth2 ou anonyme, erreurs gérées sans arrêt du service.
- Historique des positions en base : classes `BaseDeDonnees` et `DepotPositions`, tables `aircraft` et `observation`, aucune observation en double.
- API FastAPI (`uvicorn backend.main:app`) : `GET /aircraft?q=`, `GET /aircraft/{icao24}` et `GET /aircraft/{icao24}/trajectory`.
- Moteur de règles : classe abstraite `Regle`, règles R1 (délai de contact) et R2 (position ancienne), classe `MoteurRegles`.
- Pages de connexion et de recherche (`frontend/`), encore statiques.
- Intégration continue : ruff et pytest lancés à chaque pull request, obligatoires pour fusionner dans `main`.

### Supprimé
- Script `ingestion/test_opensky.py`, remplacé par le collecteur.

## [v0.3.0] — 9 novembre 2026 — Sprint 3

### Ajouté
- Nouveau dépôt public dans l'organisation `aerosafe-ipsa`, branche `main` protégée.
- Méthode Scrum documentée (`docs/scrum/`), modèles d'issue et de pull request, guide de contribution.
- Script de test de l'API OpenSky réimporté depuis l'ancien dépôt (`ingestion/test_opensky.py`).
- Conception : diagrammes de cas d'utilisation, de classes et de séquence (`docs/conception/`).
- Maquettes des écrans de connexion, recherche, fiche aéronef et dashboard (`docs/conception/maquettes/`).
- Cahier des charges V3, avec les versions V1 et V2 (`docs/cahier-des-charges/`).
- Structure du projet (`backend/`, `collector/`, `frontend/`, `tests/`) et base PostgreSQL lancée par Docker Compose.

## Sprint 2 — 21 octobre 2026 (ancien dépôt `tovkadosh/aerosafe`, archivé)

- Squelette du projet et script de test de l'API OpenSky (OAuth2, zone France). Réimporté dans ce dépôt au sprint 3.
