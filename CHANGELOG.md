# Journal des versions

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Une version par sprint ayant livré du code.

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
