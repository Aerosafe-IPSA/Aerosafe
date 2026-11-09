# Collecteur

Service qui interroge l'API OpenSky toutes les 60 secondes sur la France métropolitaine.

- `modeles.py` : classes `Aeronef` et `EtatVol` (voir `docs/conception/classes.md`)
- `collecteur.py` : classe `CollecteurOpenSky` (OAuth2, quota dépassé, valeurs manquantes)
- `__main__.py` : boucle de collecte

## Lancer la collecte

```bash
pip install -r requirements.txt
python -m collector
```

Avec `OPENSKY_CLIENT_ID` et `OPENSKY_CLIENT_SECRET` dans `.env`, l'accès se fait en OAuth2 ; sinon en mode anonyme, au quota plus faible. Une erreur d'OpenSky (quota dépassé, API injoignable) est journalisée et la collecte reprend au cycle suivant.

L'enregistrement en base arrive avec l'issue #16.
