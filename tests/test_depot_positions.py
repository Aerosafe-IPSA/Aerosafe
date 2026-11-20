"""Tests de l'enregistrement des positions, sur une base SQLite en mémoire."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import OperationalError

from backend.bdd import AircraftTable, BaseDeDonnees, ObservationTable
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol
from collector.service import ServiceCollecte

ETAT = [
    "39bd24",
    "AFR1462 ",
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


def aeronef(icao24="39bd24", callsign="AFR1462", horodatage=1762680010):
    """Fabrique un aéronef avec un seul état, à l'instant donné."""
    avion = Aeronef(icao24, callsign, "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(ETAT, horodatage))
    return avion


@pytest.fixture
def base():
    """Base SQLite vide, en mémoire, avec les tables créées."""
    return BaseDeDonnees("sqlite://")


def test_tables_et_index_crees(base):
    inspecteur = inspect(base.moteur)
    assert {"aircraft", "observation"} <= set(inspecteur.get_table_names())
    index = {i["name"]: i for i in inspecteur.get_indexes("observation")}
    assert index["ix_observation_icao24_observed_at"]["column_names"] == [
        "icao24",
        "observed_at",
    ]
    assert index["ix_observation_icao24_observed_at"]["unique"]


def test_enregistre_une_collecte(base):
    depot = DepotPositions(base)

    nouvelles = depot.enregistrer([aeronef(), aeronef("3946e2", None)])

    assert nouvelles == 2
    with base.moteur.connect() as connexion:
        ligne = connexion.execute(select(ObservationTable)).first()
    assert ligne.icao24 == "39bd24"
    assert ligne.baro_altitude == 9144.0
    assert ligne.velocity == 228.0


def test_pas_de_doublon(base):
    depot = DepotPositions(base)

    depot.enregistrer([aeronef()])
    nouvelles = depot.enregistrer([aeronef()])

    assert nouvelles == 0
    assert depot.nombre_observations("39bd24") == 1


def test_historique_conserve(base):
    depot = DepotPositions(base)

    depot.enregistrer([aeronef(horodatage=1762680010)])
    depot.enregistrer([aeronef(horodatage=1762680070)])

    assert depot.nombre_observations("39bd24") == 2


def test_aeronef_mis_a_jour(base):
    depot = DepotPositions(base)

    depot.enregistrer([aeronef(callsign=None, horodatage=1762680010)])
    depot.enregistrer([aeronef(callsign="AFR1462", horodatage=1762680070)])

    with base.moteur.connect() as connexion:
        avion = connexion.execute(select(AircraftTable)).one()
    assert avion.callsign == "AFR1462"
    assert avion.last_seen.replace(tzinfo=None) > avion.first_seen.replace(tzinfo=None)


def test_doublon_dans_une_meme_collecte(base):
    depot = DepotPositions(base)

    assert depot.enregistrer([aeronef(), aeronef()]) == 1


def test_collecte_vide(base):
    assert DepotPositions(base).enregistrer([]) == 0


def test_url_construite_depuis_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_DB", "b")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.delenv("POSTGRES_HOST", raising=False)

    assert BaseDeDonnees.url_depuis_env() == "postgresql+psycopg://u:p@localhost:5433/b"


def test_service_continue_si_la_base_ne_repond_pas(monkeypatch):
    monkeypatch.setattr("collector.service.time.sleep", lambda _: None)
    collecteur = MagicMock()
    collecteur.recuperer_etats.return_value = [aeronef()]
    depot = MagicMock()
    depot.enregistrer.side_effect = OperationalError(
        "INSERT", {}, Exception("hors ligne")
    )

    ServiceCollecte(collecteur, depot).lancer(cycles=2)

    assert depot.enregistrer.call_count == 2


def test_cycle_renvoie_le_nombre_de_nouvelles_positions(base):
    collecteur = MagicMock()
    collecteur.recuperer_etats.return_value = [aeronef(), aeronef("3946e2")]

    service = ServiceCollecte(collecteur, DepotPositions(base))

    assert service.executer_cycle() == 2
    assert service.executer_cycle() == 0
