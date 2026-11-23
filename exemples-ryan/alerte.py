"""Classe Alerte : une anomalie détectée sur un aéronef."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alerte:
    """Une anomalie détectée par une règle, avec l'explication de son déclenchement."""

    aeronef: str
    nom_regle: str
    date_heure: datetime
    valeur_observee: float
    seuil: float
    message: str
    statut: str = "en cours"
