"""R1 — Délai de contact dépassé (seuil : 300 s)."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from collector.modeles import Aeronef


class R1DelaiContact(Regle):
    """Règle R1 : aucun contact radio depuis plus de 5 minutes."""

    def __init__(self, seuil: float = 300.0) -> None:
        """Crée la règle avec son seuil en secondes."""
        super().__init__("R1", seuil)

    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une alerte si le délai depuis le dernier contact dépasse le seuil."""
        etat = aeronef.derniere_position()
        if etat is None or etat.last_contact is None:
            return None
        valeur = (etat.horodatage - etat.last_contact).total_seconds()
        if valeur <= self._seuil:
            return None
        message = f"Aucun contact depuis {valeur:.0f} s (seuil : {self._seuil:.0f} s)"
        return self._alerte(aeronef, etat, valeur, message)
