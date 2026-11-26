"""Tests des routes d'alertes et du tableau de bord, sur SQLite en mémoire."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from backend.application import ApplicationAeroSafe
from backend.bdd import AlerteTable, BaseDeDonnees
from backend.depot_alertes import DepotAlertes
from backend.depot_utilisateurs import DepotUtilisateurs
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol

T0 = datetime(2026, 11, 26, 14, 32, tzinfo=timezone.utc)


def aeronef(icao24, callsign, latitude=43.63, longitude=1.44):
    """Fabrique un aéronef avec une seule position, à l'instant T0."""
    instant = int(T0.timestamp())
    ligne = [
        icao24,
        callsign,
        "France",
        instant - 2,
        instant - 1,
        longitude,
        latitude,
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
    avion = Aeronef(icao24, callsign, "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(ligne, instant))
    return avion


def alerte(icao24, regle, minutes, valeur, seuil):
    """Fabrique une ligne de la table ``alert``, datée de T0 + minutes."""
    return {
        "icao24": icao24,
        "nom_regle": regle,
        "date_heure": T0 + timedelta(minutes=minutes),
        "valeur_observee": valeur,
        "seuil": seuil,
        "message": f"Alerte {regle} de test",
        "statut": "en cours",
    }


@pytest.fixture
def base():
    """Base de test : trois aéronefs, trois alertes, deux comptes."""
    base = BaseDeDonnees("sqlite://")
    DepotPositions(base).enregistrer(
        [
            aeronef("39bd24", "AFR1462"),
            aeronef("4ca7b3", "RYR8GH", latitude=47.2, longitude=-1.6),
            aeronef("3c6444", None, latitude=None, longitude=None),
        ]
    )
    with base.moteur.begin() as connexion:
        connexion.execute(
            insert(AlerteTable),
            [
                alerte("39bd24", "R3", 0, 18.4, 15.0),
                alerte("39bd24", "R5", 2, 80.0, 45.0),
                alerte("4ca7b3", "R3", 1, 16.0, 15.0),
            ],
        )
    depot = DepotUtilisateurs(base)
    depot.creer("utilisateur@aerosafe.fr", "motdepasse")
    depot.creer("superviseur@aerosafe.fr", "superpass", "superviseur")
    return base


@pytest.fixture
def client(base):
    """Client de test, sans connexion."""
    return TestClient(ApplicationAeroSafe(base).app)


def connexion(client, email, mot_de_passe):
    """Se connecte et renvoie l'en-tête Authorization."""
    reponse = client.post("/login", json={"email": email, "mot_de_passe": mot_de_passe})
    return {"Authorization": f"Bearer {reponse.json()['access_token']}"}


@pytest.fixture
def superviseur(client):
    """En-tête d'un compte superviseur connecté."""
    return connexion(client, "superviseur@aerosafe.fr", "superpass")


@pytest.fixture
def utilisateur(client):
    """En-tête d'un compte utilisateur connecté."""
    return connexion(client, "utilisateur@aerosafe.fr", "motdepasse")


def test_alertes_de_la_plus_recente_a_la_plus_ancienne(client, superviseur):
    alertes = client.get("/alerts", headers=superviseur).json()

    assert [a["nom_regle"] for a in alertes] == ["R5", "R3", "R3"]
    assert alertes[0]["icao24"] == "39bd24"
    assert alertes[0]["callsign"] == "AFR1462"
    assert alertes[0]["valeur_observee"] == 80.0
    assert alertes[0]["seuil"] == 45.0
    assert alertes[0]["statut"] == "en cours"


def test_alertes_limitees_et_filtrees(client, superviseur):
    assert len(client.get("/alerts?limite=2", headers=superviseur).json()) == 2
    assert len(client.get("/alerts?icao24=4CA7B3", headers=superviseur).json()) == 1
    assert client.get("/alerts?limite=0", headers=superviseur).status_code == 422


def test_statistiques(client, superviseur):
    stats = client.get("/stats", headers=superviseur).json()

    assert stats["aeronefs_suivis"] == 3
    assert stats["alertes"] == 3
    assert stats["alertes_par_regle"] == {"R1": 0, "R2": 0, "R3": 2, "R4": 0, "R5": 1}


def test_statistiques_sans_aucune_alerte():
    stats = DepotAlertes(BaseDeDonnees("sqlite://")).statistiques()

    assert stats.aeronefs_suivis == 0
    assert stats.alertes == 0
    assert stats.alertes_par_regle == {"R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0}


def test_tableau_de_bord_reserve_au_superviseur(client, utilisateur):
    assert client.get("/alerts", headers=utilisateur).status_code == 403
    assert client.get("/stats", headers=utilisateur).status_code == 403
    assert client.get("/alerts").status_code == 401
    assert client.get("/stats").status_code == 401


def test_alertes_d_un_aeronef_pour_tout_compte_connecte(client, utilisateur):
    alertes = client.get("/aircraft/39BD24/alerts", headers=utilisateur).json()

    assert [a["nom_regle"] for a in alertes] == ["R5", "R3"]
    assert client.get("/aircraft/3c6444/alerts", headers=utilisateur).json() == []
    assert client.get("/aircraft/39bd24/alerts").status_code == 401


def test_recherche_renvoie_la_derniere_position(client, utilisateur):
    avions = {
        a["icao24"]: a for a in client.get("/aircraft", headers=utilisateur).json()
    }

    assert avions["39bd24"]["latitude"] == 43.63
    assert avions["39bd24"]["longitude"] == 1.44
    assert avions["3c6444"]["latitude"] is None
