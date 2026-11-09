# AeroSafe
![CI](https://github.com/aerosafe-ipsa/aerosafe/actions/workflows/ci.yml/badge.svg)

Application de surveillance et d'analyse des données aéronautiques issues d'[OpenSky Network](https://opensky-network.org/), avec détection automatique de situations anormales.

Projet fil rouge du cours de Génie Logiciel et Développement Opérationnel — IPSA Bachelor 3.

## Équipe et méthode

Projet réalisé en **Scrum** par Tov (Scrum Master), Lucas (Product Owner), Teddy et Ryan.

- Rôles et référents : [`docs/scrum/equipe.md`](docs/scrum/equipe.md)
- Méthode, calendrier des sprints et Definition of Done : [`docs/scrum/methode.md`](docs/scrum/methode.md)
- Comptes rendus de sprint : [`docs/scrum/sprints/`](docs/scrum/sprints/)
- Cahiers des charges successifs : [`docs/cahier-des-charges/`](docs/cahier-des-charges/)
- Conception : [`docs/conception/`](docs/conception/)
- Contribuer (branches, commits, pull requests) : [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Versions : [`CHANGELOG.md`](CHANGELOG.md)

## Lancer la base de données

1. Copier le fichier d'exemple de configuration :

```bash
cp .env.example .env
```

   Sous PowerShell, utiliser `copy .env.example .env`. Ouvrir ensuite `.env` et remplacer `POSTGRES_PASSWORD` par un mot de passe de votre choix.

2. Démarrer la base :

```bash
docker compose up -d
```