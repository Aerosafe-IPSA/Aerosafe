"""R2 — Position GPS ancienne (seuil : 600 s)."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from collector.modeles import Aeronef


class R2PositionAncienne(Regle):
    """Règle R2 : position GPS non mise à jour depuis plus de 10 minutes."""

    def __init__(self, seuil: float = 600.0) -> None:
        """Crée la règle avec son seuil en secondes."""
        super().__init__("R2", seuil)

    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une alerte si la position GPS n'a pas été mise à jour depuis trop longtemps."""
        etat = aeronef.derniere_position()
        if etat is None or etat.time_position is None:
            return None
        valeur = (etat.horodatage - etat.time_position).total_seconds()
        if valeur <= self._seuil:
            return None
        message = f"Position GPS vieille de {valeur:.0f} s (seuil : {self._seuil:.0f} s)"
        return self._alerte(aeronef, etat, valeur, message)
