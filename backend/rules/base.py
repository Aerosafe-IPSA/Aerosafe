"""Classe abstraite Regle — interface commune à toutes les règles."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.rules.alerte import Alerte
from collector.modeles import Aeronef, EtatVol


class Regle(ABC):
    """Classe de base de toutes les règles du moteur."""

    def __init__(self, nom: str, seuil: float) -> None:
        """Enregistre le nom court de la règle (ex. 'R3') et son seuil."""
        self._nom = nom
        self._seuil = seuil

    @abstractmethod
    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une Alerte si la règle se déclenche, sinon None."""

    def _alerte(
        self, aeronef: Aeronef, etat: EtatVol, valeur: float, message: str
    ) -> Alerte:
        """Fabrique l'alerte de cette règle pour l'état donné."""
        return Alerte(
            aeronef.icao24, self._nom, etat.horodatage, valeur, self._seuil, message
        )
