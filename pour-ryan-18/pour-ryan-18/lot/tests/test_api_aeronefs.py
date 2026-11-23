"""Tests de l'API des aéronefs, sur une base SQLite en mémoire."""

import pytest
from fastapi.testclient import TestClient

from backend.application import ApplicationAeroSafe
from backend.bdd import BaseDeDonnees
from backend.depot_utilisateurs import DepotUtilisateurs
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol

T0 = 1762680000


def aeronef(icao24, callsign, horodatage, altitude=9144.0, au_sol=False, contact=None):
    """Fabrique un aéronef avec un seul état, à l'instant donné."""
    etat = [
        icao24,
        callsign,
        "France",
        horodatage - 2,
        contact if contact is not None else horodatage - 1,
        1.44,
        43.63,
        altitude,
        au_sol,
        228.0,
        200.0,
        -0.3,
        None,
        9200.0,
        "1000",
        False,
        0,
    ]
    avion = Aeronef(icao24, callsign, "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(etat, horodatage))
    return avion


@pytest.fixture
def client():
    """API branchée sur une base de test contenant trois aéronefs, client connecté."""
    base = BaseDeDonnees("sqlite://")
    depot = DepotPositions(base)
    # AFR1462 : trois positions, une par minute, en descente
    for minute, altitude in enumerate([9500.0, 9300.0, 9144.0]):
        depot.enregistrer([aeronef("39bd24", "AFR1462", T0 + 60 * minute, altitude)])
    # AFR6204 : au sol
    depot.enregistrer([aeronef("398b1f", "AFR6204", T0 + 120, None, au_sol=True)])
    # RYR8GH : plus aucun message depuis 7 minutes
    depot.enregistrer([aeronef("4ca7b3", "RYR8GH", T0 + 120, contact=T0 + 120 - 420)])
    DepotUtilisateurs(base).creer("test@aerosafe.fr", "motdepasse")
    client = TestClient(ApplicationAeroSafe(base).app)
    connexion = client.post(
        "/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "motdepasse"}
    )
    client.headers["Authorization"] = f"Bearer {connexion.json()['access_token']}"
    return client


def test_recherche_par_indicatif_sans_tenir_compte_de_la_casse(client):
    reponse = client.get("/aircraft", params={"q": "afr"})

    assert reponse.status_code == 200
    assert {a["callsign"] for a in reponse.json()} == {"AFR1462", "AFR6204"}


def test_recherche_par_morceau_de_code_icao24(client):
    resultats = client.get("/aircraft", params={"q": "39BD"}).json()

    assert [a["icao24"] for a in resultats] == ["39bd24"]
    assert resultats[0]["pays_origine"] == "France"
    assert resultats[0]["altitude"] == 9144.0


def test_recherche_sans_texte_renvoie_tous_les_aeronefs(client):
    assert len(client.get("/aircraft").json()) == 3


def test_recherche_sans_resultat(client):
    assert client.get("/aircraft", params={"q": "zzz"}).json() == []


def test_recherche_limite_le_nombre_de_resultats(client):
    assert len(client.get("/aircraft", params={"limite": 2}).json()) == 2
    assert client.get("/aircraft", params={"limite": 0}).status_code == 422


def test_caractere_joker_non_interprete(client):
    assert client.get("/aircraft", params={"q": "%"}).json() == []


def test_statuts(client):
    statuts = {a["callsign"]: a["statut"] for a in client.get("/aircraft").json()}

    assert statuts == {
        "AFR1462": "En vol",
        "AFR6204": "Au sol",
        "RYR8GH": "Contact perdu",
    }


def test_fiche_d_un_aeronef(client):
    fiche = client.get("/aircraft/39BD24").json()

    assert fiche["callsign"] == "AFR1462"
    assert fiche["statut"] == "En vol"
    assert fiche["nombre_positions"] == 3
    assert fiche["derniere_position"]["altitude"] == 9144.0
    assert fiche["derniere_position"]["vitesse"] == 228.0


def test_fiche_aeronef_inconnu(client):
    reponse = client.get("/aircraft/ffffff")

    assert reponse.status_code == 404
    assert reponse.json()["detail"] == "Aéronef inconnu"


def test_trajet_trie_par_date(client):
    positions = client.get("/aircraft/39bd24/trajectory").json()

    dates = [p["horodatage"] for p in positions]
    assert len(positions) == 3
    assert dates == sorted(dates)
    assert [p["altitude"] for p in positions] == [9500.0, 9300.0, 9144.0]


def test_trajet_limite_aux_dernieres_minutes(client):
    positions = client.get("/aircraft/39bd24/trajectory", params={"minutes": 1}).json()

    assert [p["altitude"] for p in positions] == [9300.0, 9144.0]


def test_trajet_aeronef_inconnu(client):
    assert client.get("/aircraft/ffffff/trajectory").status_code == 404


def test_routes_refusees_sans_jeton(client):
    del client.headers["Authorization"]

    assert client.get("/aircraft").status_code == 401
    assert client.get("/aircraft/39bd24").status_code == 401
    assert client.get("/aircraft/39bd24/trajectory").status_code == 401
