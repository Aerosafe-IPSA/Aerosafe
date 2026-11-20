"""Assemblage de l'application web AeroSafe."""

from __future__ import annotations

from fastapi import FastAPI

from backend.api_aeronefs import ApiAeronefs
from backend.bdd import BaseDeDonnees
from backend.depot_aeronefs import DepotAeronefs


class ApplicationAeroSafe:
    """Crée l'application FastAPI et y branche les routes de chaque domaine.

    Pour ajouter un domaine (connexion, alertes, règles), il suffit de créer sa
    classe d'API et d'ajouter son routeur dans ``_brancher_routes``.
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
        self._app.include_router(ApiAeronefs(DepotAeronefs(self._base)).routeur)

    @property
    def app(self) -> FastAPI:
        """Application FastAPI, à donner au serveur uvicorn."""
        return self._app
