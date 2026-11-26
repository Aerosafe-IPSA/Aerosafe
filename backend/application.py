"""Assemblage de l'application web AeroSafe."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.api_aeronefs import ApiAeronefs
from backend.api_connexion import ApiConnexion
from backend.bdd import BaseDeDonnees
from backend.depot_aeronefs import DepotAeronefs
from backend.depot_utilisateurs import DepotUtilisateurs


class ApplicationAeroSafe:
    """Crée l'application FastAPI et y branche les routes de chaque domaine.

    Toutes les routes de données, sauf ``/login``, exigent un jeton valide
    (exigence BNF-03). Les pages de l'interface sont servies sous ``/app``.
    Pour ajouter un domaine (alertes, règles), il suffit de créer sa classe d'API
    et d'ajouter son routeur dans ``_brancher_routes``.
    """

    VERSION = "0.4.0"
    DOSSIER_INTERFACE = Path(__file__).resolve().parent.parent / "frontend"

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
        self._brancher_interface()

    def _brancher_routes(self) -> None:
        """Ajoute à l'application les routes de chaque domaine."""
        connexion = ApiConnexion(DepotUtilisateurs(self._base))
        compte_connecte = [Depends(connexion.garde.verifier)]
        self._app.include_router(connexion.routeur)
        self._app.include_router(
            ApiAeronefs(DepotAeronefs(self._base)).routeur, dependencies=compte_connecte
        )

    def _brancher_interface(self) -> None:
        """Sert les pages du dossier ``frontend`` sous ``/app``.

        Les pages sont publiques ; ce sont les données, demandées à l'API par
        chaque page, qui exigent un jeton. La racine du site renvoie vers la page
        de connexion.
        """
        if self.DOSSIER_INTERFACE.is_dir():
            self._app.mount(
                "/app",
                StaticFiles(directory=self.DOSSIER_INTERFACE, html=True),
                name="interface",
            )
        self._app.add_api_route(
            "/", self.accueil, methods=["GET"], include_in_schema=False
        )

    def accueil(self) -> RedirectResponse:
        """Renvoie la racine du site vers la page de connexion."""
        return RedirectResponse("/app/login.html")

    @property
    def app(self) -> FastAPI:
        """Application FastAPI, à donner au serveur uvicorn."""
        return self._app
