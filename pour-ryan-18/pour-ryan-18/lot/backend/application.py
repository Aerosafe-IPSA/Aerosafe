"""Assemblage de l'application web AeroSafe."""

from __future__ import annotations

from fastapi import Depends, FastAPI

from backend.api_aeronefs import ApiAeronefs
from backend.api_connexion import ApiConnexion
from backend.bdd import BaseDeDonnees
from backend.depot_aeronefs import DepotAeronefs
from backend.depot_utilisateurs import DepotUtilisateurs


class ApplicationAeroSafe:
    """Crée l'application FastAPI et y branche les routes de chaque domaine.

    Toutes les routes, sauf ``/login``, exigent un jeton valide (exigence BNF-03).
    Pour ajouter un domaine (alertes, règles), il suffit de créer sa classe d'API
    et d'ajouter son routeur dans ``_brancher_routes``.
    """

    VERSION = "0.4.0"

    def __init__(self, base: BaseDeDonnees | None = None) -> None:
        """Prépare l'application.

        Args:
            base: connexion à la base ; par défaut celle décrite par le fichier .env.
        """
        self._base = base or BaseDeDonnees()
        self._app = FastAPI(
            title="AeroSafe",
            description="Surveillance et analyse des données aéronautiques OpenSky.",
            version=self.VERSION,
        )
        self._brancher_routes()

    def _brancher_routes(self) -> None:
        """Ajoute à l'application les routes de chaque domaine."""
        connexion = ApiConnexion(DepotUtilisateurs(self._base))
        compte_connecte = [Depends(connexion.garde.verifier)]
        self._app.include_router(connexion.routeur)
        self._app.include_router(
            ApiAeronefs(DepotAeronefs(self._base)).routeur, dependencies=compte_connecte
        )

    @property
    def app(self) -> FastAPI:
        """Application FastAPI, à donner au serveur uvicorn."""
        return self._app
