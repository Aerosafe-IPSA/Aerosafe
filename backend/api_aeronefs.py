"""Routes de l'API pour rechercher un aéronef et récupérer son trajet."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.depot_aeronefs import DepotAeronefs
from backend.schemas_aeronefs import FicheAeronef, PositionTrajet, ResumeAeronef


class ApiAeronefs:
    """Expose les aéronefs et leurs trajets sous l'adresse ``/aircraft``.

    Les routes ne contiennent aucune logique métier : elles délèguent la lecture
    au ``DepotAeronefs`` et transforment une absence en erreur 404.
    """

    def __init__(self, depot: DepotAeronefs) -> None:
        """Déclare les trois routes.

        Args:
            depot: le dépôt qui lit les aéronefs en base.
        """
        self._depot = depot
        self._routeur = APIRouter(prefix="/aircraft", tags=["Aéronefs"])
        self._routeur.add_api_route(
            "",
            self.rechercher,
            methods=["GET"],
            response_model=list[ResumeAeronef],
            summary="Rechercher un aéronef par code ICAO24 ou par indicatif",
        )
        self._routeur.add_api_route(
            "/{icao24}",
            self.fiche,
            methods=["GET"],
            response_model=FicheAeronef,
            summary="Fiche d'un aéronef",
        )
        self._routeur.add_api_route(
            "/{icao24}/trajectory",
            self.trajet,
            methods=["GET"],
            response_model=list[PositionTrajet],
            summary="Positions successives d'un aéronef, triées par date",
        )

    @property
    def routeur(self) -> APIRouter:
        """Routeur FastAPI à brancher sur l'application."""
        return self._routeur

    def rechercher(
        self,
        q: str = Query("", description="Morceau de code ICAO24 ou d'indicatif"),
        limite: int = Query(
            50, ge=1, le=200, description="Nombre maximal de résultats"
        ),
    ) -> list[ResumeAeronef]:
        """Renvoie les aéronefs dont le code ou l'indicatif contient ``q``."""
        return self._depot.rechercher(q, limite)

    def fiche(self, icao24: str) -> FicheAeronef:
        """Renvoie la fiche d'un aéronef, ou une erreur 404 s'il est inconnu."""
        fiche = self._depot.trouver(icao24)
        if fiche is None:
            raise HTTPException(status_code=404, detail="Aéronef inconnu")
        return fiche

    def trajet(
        self,
        icao24: str,
        minutes: Optional[int] = Query(
            None,
            ge=1,
            le=10080,
            description="Durée à remonter depuis la dernière position ; tout l'historique par défaut",
        ),
    ) -> list[PositionTrajet]:
        """Renvoie le trajet d'un aéronef, ou une erreur 404 s'il est inconnu."""
        positions = self._depot.trajet(icao24, minutes)
        if positions is None:
            raise HTTPException(status_code=404, detail="Aéronef inconnu")
        return positions
