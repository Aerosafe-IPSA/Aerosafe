"""R5 — Changement de cap brutal (seuil : 45°)."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from backend.rules.ecart_angulaire import ecart_angulaire
from collector.modeles import Aeronef

INTERVALLE_MAX = 90.0


class R5ChangementCap(Regle):
    """Règle R5 : écart de cap entre les deux dernières observations dépasse 45°."""

    def __init__(self, seuil: float = 45.0) -> None:
        """Crée la règle avec son seuil en degrés."""
        super().__init__("R5", seuil)

    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une alerte si le changement de cap dépasse le seuil."""
        etat = aeronef.derniere_position()
        precedent = aeronef.etat_precedent()

        if etat is None or precedent is None:
            return None
        if etat.cap is None or precedent.cap is None:
            return None

        # Ignore les comparaisons avec un trop grand écart temporel (collecte manquée)
        intervalle = (etat.horodatage - precedent.horodatage).total_seconds()
        if not (0 < intervalle <= INTERVALLE_MAX):
            return None

        valeur = ecart_angulaire(etat.cap, precedent.cap)
        if valeur <= self._seuil:
            return None
        message = f"Changement de cap de {valeur:.1f}° (seuil : {self._seuil:.0f}°)"
        return self._alerte(aeronef, etat, valeur, message)
