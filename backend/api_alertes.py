"""Routes de l'API pour les alertes et les chiffres du tableau de bord."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from backend.depot_alertes import DepotAlertes
from backend.schemas_alertes import AlerteVue, Statistiques


class ApiAlertes:
    """Expose les alertes à l'interface.

    Deux routeurs, car les droits diffèrent : ``routeur`` (``/alerts`` et
    ``/stats``) est réservé au superviseur, ``routeur_aeronef``
    (``/aircraft/{icao24}/alerts``) est ouvert à tout compte connecté.
    Le contrôle d'accès est ajouté par ``ApplicationAeroSafe``.
    """

    def __init__(self, depot: DepotAlertes) -> None:
        """Déclare les routes.

        Args:
            depot: le dépôt qui lit les alertes en base.
        """
        self._depot = depot
        self._routeur = APIRouter(tags=["Alertes"])
        self._routeur.add_api_route(
            "/alerts",
            self.alertes,
            methods=["GET"],
            response_model=list[AlerteVue],
            summary="Alertes les plus récentes, tous aéronefs confondus",
        )
        self._routeur.add_api_route(
            "/stats",
            self.statistiques,
            methods=["GET"],
            response_model=Statistiques,
            summary="Chiffres du tableau de bord",
        )
        self._routeur_aeronef = APIRouter(tags=["Alertes"])
        self._routeur_aeronef.add_api_route(
            "/aircraft/{icao24}/alerts",
            self.alertes_aeronef,
            methods=["GET"],
            response_model=list[AlerteVue],
            summary="Alertes d'un aéronef",
        )

    @property
    def routeur(self) -> APIRouter:
        """Routes du tableau de bord, à réserver au superviseur."""
        return self._routeur

    @property
    def routeur_aeronef(self) -> APIRouter:
        """Route des alertes d'un aéronef, pour tout compte connecté."""
        return self._routeur_aeronef

    def alertes(
        self,
        limite: int = Query(50, ge=1, le=200, description="Nombre maximal d'alertes"),
        icao24: Optional[str] = Query(
            None, description="Pour ne garder que les alertes d'un aéronef"
        ),
    ) -> list[AlerteVue]:
        """Renvoie les alertes, de la plus récente à la plus ancienne."""
        return self._depot.lister(icao24, limite)

    def statistiques(self) -> Statistiques:
        """Renvoie le nombre d'aéronefs suivis et d'alertes, au total et par règle."""
        return self._depot.statistiques()

    def alertes_aeronef(
        self,
        icao24: str,
        limite: int = Query(50, ge=1, le=200, description="Nombre maximal d'alertes"),
    ) -> list[AlerteVue]:
        """Renvoie les alertes d'un aéronef ; liste vide s'il n'en a aucune."""
        return self._depot.lister(icao24, limite)
