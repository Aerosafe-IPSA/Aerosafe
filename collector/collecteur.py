"""Récupération des données de vol sur l'API OpenSky Network."""

from __future__ import annotations

import logging
import os
import time

import requests

from collector.modeles import Aeronef, EtatVol

logger = logging.getLogger(__name__)

URL_API = "https://opensky-network.org/api/states/all"
URL_JETON = (
    "https://auth.opensky-network.org/auth/realms/opensky-network"
    "/protocol/openid-connect/token"
)
# France métropolitaine (cahier des charges, périmètre du projet)
ZONE_FRANCE = {"lamin": 41.3, "lomin": -5.2, "lamax": 51.1, "lomax": 9.6}


class ErreurOpenSky(Exception):
    """Erreur renvoyée quand l'API OpenSky ne peut pas fournir de données."""


class CollecteurOpenSky:
    """Interroge l'API OpenSky et transforme la réponse en objets ``Aeronef``.

    Avec ``OPENSKY_CLIENT_ID`` et ``OPENSKY_CLIENT_SECRET`` (fichier .env),
    l'accès se fait en OAuth2 ; sinon en mode anonyme, au quota plus faible.
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        zone: dict | None = None,
        session: requests.Session | None = None,
    ) -> None:
        """Prépare le collecteur.

        Args:
            client_id: identifiant OAuth2 ; par défaut la variable OPENSKY_CLIENT_ID.
            client_secret: secret OAuth2 ; par défaut la variable OPENSKY_CLIENT_SECRET.
            zone: limites lamin, lomin, lamax, lomax ; par défaut la France.
            session: session HTTP, remplaçable dans les tests.
        """
        self._url_api = URL_API
        self._zone = zone or ZONE_FRANCE
        self._client_id = client_id or os.getenv("OPENSKY_CLIENT_ID")
        self._client_secret = client_secret or os.getenv("OPENSKY_CLIENT_SECRET")
        self._session = session or requests.Session()
        self._jeton: str | None = None
        self._expiration_jeton = 0.0

    @property
    def authentifie(self) -> bool:
        """Indique si des identifiants OAuth2 sont configurés."""
        return bool(self._client_id and self._client_secret)

    def _rafraichir_jeton(self) -> None:
        """Demande un nouveau jeton OAuth2 s'il est absent ou bientôt expiré."""
        if not self.authentifie or time.time() < self._expiration_jeton - 60:
            return
        reponse = self._session.post(
            URL_JETON,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=15,
        )
        reponse.raise_for_status()
        contenu = reponse.json()
        self._jeton = contenu["access_token"]
        self._expiration_jeton = time.time() + contenu.get("expires_in", 1800)

    def recuperer_etats(self) -> list[Aeronef]:
        """Récupère l'état actuel de tous les aéronefs de la zone.

        Returns:
            Un ``Aeronef`` par avion, contenant son état le plus récent.

        Raises:
            ErreurOpenSky: quota dépassé (429), erreur HTTP ou API injoignable.
        """
        try:
            self._rafraichir_jeton()
            entetes = {"Authorization": f"Bearer {self._jeton}"} if self._jeton else {}
            reponse = self._session.get(
                self._url_api, params=self._zone, headers=entetes, timeout=30
            )
        except requests.RequestException as erreur:
            raise ErreurOpenSky(f"API OpenSky injoignable : {erreur}") from erreur

        if reponse.status_code == 429:
            attente = reponse.headers.get("X-Rate-Limit-Retry-After-Seconds", "?")
            raise ErreurOpenSky(f"Quota OpenSky dépassé, réessayer dans {attente} s")
        if reponse.status_code != 200:
            raise ErreurOpenSky(
                f"Réponse OpenSky inattendue : HTTP {reponse.status_code}"
            )

        donnees = reponse.json()
        horodatage = donnees.get("time")
        aeronefs = []
        for etat in donnees.get("states") or []:
            if not etat or not etat[0]:
                continue
            callsign = (etat[1] or "").strip() or None
            aeronef = Aeronef(etat[0], callsign, etat[2])
            aeronef.ajouter_etat(EtatVol.depuis_opensky(etat, horodatage))
            aeronefs.append(aeronef)
        logger.info("%d aéronefs récupérés", len(aeronefs))
        return aeronefs

    def recuperer_aeronef(self, icao24: str) -> Aeronef | None:
        """Récupère un aéronef précis de la zone par son adresse ICAO24.

        Args:
            icao24: adresse ICAO24 recherchée, sans tenir compte de la casse.

        Returns:
            L'aéronef s'il est présent dans la zone, sinon None.
        """
        recherche = icao24.lower()
        for aeronef in self.recuperer_etats():
            if aeronef.icao24 == recherche:
                return aeronef
        return None
