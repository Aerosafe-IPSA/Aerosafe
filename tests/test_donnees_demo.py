"""Tests des données de secours : export puis rechargement, sur SQLite en mémoire."""

from backend.bdd import BaseDeDonnees
from collector.depot_positions import DepotPositions
from collector.donnees_demo import charger, exporter
from collector.modeles import Aeronef, EtatVol

# Une ligne au format OpenSky (17 valeurs), avec un indicatif absent
ETAT = [
    "39bd24",
    None,
    "France",
    1762680000,
    1762680005,
    1.44,
    43.63,
    9144.0,
    False,
    228.0,
    200.0,
    -0.3,
    None,
    9200.0,
    "1000",
    False,
    0,
]


def aeronef(icao24, horodatage):
    """Fabrique un aéronef avec un seul état, à l'instant donné."""
    avion = Aeronef(icao24, None, "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(ETAT, horodatage))
    return avion


def test_export_puis_chargement(tmp_path):
    source = BaseDeDonnees("sqlite://")
    depot = DepotPositions(source)
    depot.enregistrer([aeronef("39bd24", 1762680010), aeronef("3946e2", 1762680010)])
    depot.enregistrer([aeronef("39bd24", 1762680070)])
    fichier = tmp_path / "positions.csv"

    assert exporter(source, fichier) == 3

    cible = BaseDeDonnees("sqlite://")
    assert charger(cible, fichier) == 3
    assert DepotPositions(cible).nombre_observations("39bd24") == 2


def test_chargement_sans_doublon(tmp_path):
    source = BaseDeDonnees("sqlite://")
    DepotPositions(source).enregistrer([aeronef("39bd24", 1762680010)])
    fichier = tmp_path / "positions.csv"
    exporter(source, fichier)

    cible = BaseDeDonnees("sqlite://")
    charger(cible, fichier)

    assert charger(cible, fichier) == 0