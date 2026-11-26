"""Formats des réponses de l'API pour les aéronefs et leurs trajets.

Les noms des champs reprennent ceux du diagramme de classes (``Aeronef``,
``EtatVol``) ; les unités sont celles d'OpenSky : mètres, m/s et degrés.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResumeAeronef(BaseModel):
    """Une ligne de résultat de recherche : l'aéronef et son dernier état connu."""

    icao24: str
    callsign: Optional[str]
    pays_origine: Optional[str]
    statut: str
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    dernier_contact: Optional[datetime]
    derniere_observation: datetime


class PositionTrajet(BaseModel):
    """Une position du trajet d'un aéronef, à un instant donné."""

    horodatage: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    vitesse: Optional[float]
    cap: Optional[float]
    taux_vertical: Optional[float]
    au_sol: bool


class FicheAeronef(BaseModel):
    """Le détail d'un aéronef : identité, statut et dernière position connue."""

    icao24: str
    callsign: Optional[str]
    pays_origine: Optional[str]
    statut: str
    premiere_observation: datetime
    derniere_observation: datetime
    dernier_contact: Optional[datetime]
    nombre_positions: int
    derniere_position: Optional[PositionTrajet]
