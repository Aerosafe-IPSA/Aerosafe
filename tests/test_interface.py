"""Tests du service des pages de l'interface par l'API."""

import pytest
from fastapi.testclient import TestClient

from backend.application import ApplicationAeroSafe
from backend.bdd import BaseDeDonnees


@pytest.fixture
def client():
    """API branchée sur une base de test vide."""
    return TestClient(ApplicationAeroSafe(BaseDeDonnees("sqlite://")).app)


def test_page_de_connexion_servie_sans_jeton(client):
    reponse = client.get("/app/login.html")

    assert reponse.status_code == 200
    assert "text/html" in reponse.headers["content-type"]


def test_client_javascript_servi(client):
    reponse = client.get("/app/api.js")

    assert reponse.status_code == 200
    assert "class ClientApi" in reponse.text


def test_racine_renvoie_vers_la_connexion(client):
    reponse = client.get("/", follow_redirects=False)

    assert reponse.status_code in (302, 307)
    assert reponse.headers["location"] == "/app/login.html"


def test_page_inconnue(client):
    assert client.get("/app/nexiste-pas.html").status_code == 404


def test_les_donnees_restent_protegees(client):
    assert client.get("/aircraft").status_code == 401
