"""R3 — Variation brutale d'altitude (seuil : 15 m/s)."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from collector.modeles import Aeronef


class R3VariationAltitude(Regle):
    """Règle R3 : le taux vertical dépasse 15 m/s, en montée ou en descente."""

    def __init__(self, seuil: float = 15.0) -> None:
        """Crée la règle avec son seuil en m/s."""
        super().__init__("R3", seuil)

    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une alerte si le dernier taux vertical dépasse le seuil."""
        etat = aeronef.derniere_position()
        if etat is None or etat.taux_vertical is None:
            return None
        valeur = abs(etat.taux_vertical)
        if valeur <= self._seuil:
            return None
        message = f"Taux vertical de {valeur:.1f} m/s (seuil : {self._seuil:.0f} m/s)"
        return self._alerte(aeronef, etat, valeur, message)
