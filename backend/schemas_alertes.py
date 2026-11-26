"""Formats des réponses de l'API pour les alertes et le tableau de bord."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlerteVue(BaseModel):
    """Une alerte telle qu'elle est affichée dans l'interface."""

    icao24: str
    callsign: Optional[str]
    nom_regle: str
    date_heure: datetime
    valeur_observee: float
    seuil: float
    message: str
    statut: str


class Statistiques(BaseModel):
    """Les chiffres affichés en haut du tableau de bord."""

    aeronefs_suivis: int
    alertes: int
    alertes_par_regle: dict[str, int]
