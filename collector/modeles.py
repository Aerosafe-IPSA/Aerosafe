"""Objets métier manipulés par le collecteur et le moteur de règles.

Ces classes suivent le diagramme de classes (docs/conception/classes.md) :
un ``Aeronef`` garde l'historique de ses ``EtatVol`` successifs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def _horodatage(secondes: float | None) -> datetime | None:
    """Convertit un horodatage Unix (secondes) en date UTC, ou renvoie None."""
    if secondes is None:
        return None
    return datetime.fromtimestamp(secondes, tz=timezone.utc)


@dataclass
class EtatVol:
    """Instantané de l'état d'un aéronef à un moment donné.

    Les unités sont celles d'OpenSky : mètres, mètres par seconde et degrés.
    Chaque valeur peut être ``None`` : les données ADS-B sont souvent incomplètes.
    """

    horodatage: datetime
    latitude: float | None
    longitude: float | None
    altitude: float | None
    vitesse: float | None
    cap: float | None
    taux_vertical: float | None
    au_sol: bool
    last_contact: datetime | None
    time_position: datetime | None

    @classmethod
    def depuis_opensky(cls, etat: list, horodatage: int) -> EtatVol:
        """Construit un état à partir d'une ligne ``states`` de l'API OpenSky.

        Args:
            etat: liste de 17 valeurs renvoyée par l'API pour un aéronef.
            horodatage: champ ``time`` de la réponse (secondes Unix).

        Returns:
            L'état de vol correspondant.
        """
        return cls(
            horodatage=_horodatage(horodatage),
            latitude=etat[6],
            longitude=etat[5],
            altitude=etat[7],
            vitesse=etat[9],
            cap=etat[10],
            taux_vertical=etat[11],
            au_sol=bool(etat[8]),
            last_contact=_horodatage(etat[4]),
            time_position=_horodatage(etat[3]),
        )


class Aeronef:
    """Aéronef identifié par son adresse ICAO24, avec l'historique de ses états."""

    def __init__(
        self, icao24: str, callsign: str | None, pays_origine: str | None
    ) -> None:
        """Crée un aéronef sans historique.

        Args:
            icao24: adresse ICAO24 (6 caractères hexadécimaux), identifiant stable.
            callsign: indicatif de vol, ou None s'il n'est pas transmis.
            pays_origine: pays d'immatriculation.
        """
        self.icao24 = icao24
        self.callsign = callsign
        self.pays_origine = pays_origine
        self._historique: list[EtatVol] = []

    def ajouter_etat(self, etat: EtatVol) -> None:
        """Ajoute un état à la fin de l'historique."""
        self._historique.append(etat)

    def derniere_position(self) -> EtatVol | None:
        """Renvoie l'état le plus récent, ou None si l'historique est vide."""
        return self._historique[-1] if self._historique else None

    def etat_precedent(self) -> EtatVol | None:
        """Renvoie l'avant-dernier état, utile aux règles R3 à R5, ou None."""
        return self._historique[-2] if len(self._historique) >= 2 else None

    def __repr__(self) -> str:
        """Représentation lisible pour le débogage."""
        return f"Aeronef({self.icao24!r}, {self.callsign!r})"
