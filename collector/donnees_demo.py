"""Données de secours pour la démo, si OpenSky ne répond pas.

Usage :
    python -m collector.donnees_demo exporter   # base -> data/demo/positions.csv
    python -m collector.donnees_demo charger    # data/demo/positions.csv -> base
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select

from backend.bdd import AircraftTable, BaseDeDonnees, ObservationTable
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol

FICHIER = Path("data/demo/positions.csv")


def exporter(base: BaseDeDonnees, chemin: Path = FICHIER) -> int:
    """Copie toutes les positions de la base dans un fichier CSV.

    Args:
        base: base de données à lire.
        chemin: fichier CSV à écrire.

    Returns:
        Le nombre de positions exportées.
    """
    requete = (
        select(
            ObservationTable.icao24,
            AircraftTable.callsign,
            AircraftTable.origin_country,
            ObservationTable.observed_at,
            ObservationTable.latitude,
            ObservationTable.longitude,
            ObservationTable.baro_altitude,
            ObservationTable.velocity,
            ObservationTable.true_track,
            ObservationTable.vertical_rate,
            ObservationTable.on_ground,
            ObservationTable.last_contact,
            ObservationTable.time_position,
        )
        .join(AircraftTable, AircraftTable.icao24 == ObservationTable.icao24)
        .order_by(ObservationTable.observed_at)
    )
    chemin.parent.mkdir(parents=True, exist_ok=True)
    nombre = 0
    with base.moteur.connect() as connexion:
        resultat = connexion.execute(requete)
        with chemin.open("w", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.writer(fichier)
            ecrivain.writerow(resultat.keys())
            for ligne in resultat:
                ecrivain.writerow(ligne)
                nombre += 1
    return nombre


def _nombre(texte: str) -> float | None:
    """Convertit une case du CSV en nombre, ou None si elle est vide."""
    return float(texte) if texte else None


def _date(texte: str) -> datetime | None:
    """Convertit une case du CSV en date, ou None si elle est vide."""
    return datetime.fromisoformat(texte) if texte else None


def charger(base: BaseDeDonnees, chemin: Path = FICHIER) -> int:
    """Enregistre en base les positions d'un fichier CSV créé par ``exporter``.

    Les positions déjà présentes sont ignorées : on peut charger deux fois
    le même fichier sans créer de doublon.

    Args:
        base: base de données à remplir.
        chemin: fichier CSV à lire.

    Returns:
        Le nombre de nouvelles positions enregistrées.
    """
    collectes: dict[datetime, list[Aeronef]] = {}
    with chemin.open(newline="", encoding="utf-8") as fichier:
        for ligne in csv.DictReader(fichier):
            etat = EtatVol(
                horodatage=_date(ligne["observed_at"]),
                latitude=_nombre(ligne["latitude"]),
                longitude=_nombre(ligne["longitude"]),
                altitude=_nombre(ligne["baro_altitude"]),
                vitesse=_nombre(ligne["velocity"]),
                cap=_nombre(ligne["true_track"]),
                taux_vertical=_nombre(ligne["vertical_rate"]),
                au_sol=ligne["on_ground"] == "True",
                last_contact=_date(ligne["last_contact"]),
                time_position=_date(ligne["time_position"]),
            )
            aeronef = Aeronef(
                ligne["icao24"], ligne["callsign"] or None, ligne["origin_country"] or None
            )
            aeronef.ajouter_etat(etat)
            collectes.setdefault(etat.horodatage, []).append(aeronef)

    depot = DepotPositions(base)
    return sum(depot.enregistrer(aeronefs) for aeronefs in collectes.values())


def main() -> None:
    """Lance l'export ou le chargement selon le mot donné en ligne de commande."""
    load_dotenv()
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in ("exporter", "charger"):
        print("Usage : python -m collector.donnees_demo exporter|charger")
        sys.exit(1)
    base = BaseDeDonnees()
    if action == "exporter":
        print(f"{exporter(base)} positions exportées dans {FICHIER}")
    else:
        print(f"{charger(base)} positions chargées en base")


if __name__ == "__main__":
    main()