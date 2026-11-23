"""
Tests d'intégration pour les routes d'authentification (/login, /me, /superviseur).
On utilise TestClient (FastAPI) avec une base SQLite en mémoire pour ne pas
dépendre d'un Postgres local ou CI.
"""

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.application import ApplicationAeroSafe
from backend.bdd import BaseDeDonnees, UtilisateurTable
from backend.creer_compte import CreateurCompte
from backend.depot_utilisateurs import CompteExistantError, DepotUtilisateurs
from backend.security import ConfigurationManquanteError, ServiceAuthentification


@pytest.fixture
def base():
    """Base SQLite en mémoire avec un utilisateur et un superviseur de test."""
    base = BaseDeDonnees("sqlite://")
    depot = DepotUtilisateurs(base)
    depot.creer("test@aerosafe.fr", "motdepasse")
    depot.creer("superviseur@aerosafe.fr", "superpass", "superviseur")
    return base


@pytest.fixture
def client(base):
    """TestClient branché sur la base de test."""
    return TestClient(ApplicationAeroSafe(base).app)


def jeton(client, email="test@aerosafe.fr", mot_de_passe="motdepasse"):
    """Se connecte et renvoie l'en-tête Authorization à utiliser ensuite."""
    rep = client.post("/login", json={"email": email, "mot_de_passe": mot_de_passe})
    return {"Authorization": f"Bearer {rep.json()['access_token']}"}


def test_connexion_reussie(client):
    rep = client.post(
        "/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "motdepasse"}
    )
    assert rep.status_code == 200
    assert "access_token" in rep.json()
    assert rep.json()["token_type"] == "bearer"


def test_mauvais_mot_de_passe(client):
    rep = client.post(
        "/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "mauvais"}
    )
    assert rep.status_code == 401


def test_email_inconnu_meme_message_que_mauvais_mot_de_passe(client):
    inconnu = client.post(
        "/login", json={"email": "personne@aerosafe.fr", "mot_de_passe": "motdepasse"}
    )
    mauvais = client.post(
        "/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "mauvais"}
    )
    assert inconnu.status_code == 401
    assert inconnu.json() == mauvais.json()


def test_acces_superviseur_refuse_a_utilisateur(client):
    # D'abord on récupère un token utilisateur normal
    rep = client.get("/superviseur", headers=jeton(client))
    assert rep.status_code == 403


def test_acces_superviseur_autorise(client):
    entetes = jeton(client, "superviseur@aerosafe.fr", "superpass")
    rep = client.get("/superviseur", headers=entetes)
    assert rep.status_code == 200
    assert "superviseur@aerosafe.fr" in rep.json()["message"]


def test_me_renvoie_le_compte_connecte(client):
    rep = client.get("/me", headers=jeton(client))
    assert rep.json() == {"email": "test@aerosafe.fr", "role": "utilisateur"}


def test_route_protegee_sans_jeton(client):
    assert client.get("/me").status_code == 401


def test_jeton_invalide_ou_falsifie(client):
    assert (
        client.get("/me", headers={"Authorization": "Bearer nimporte"}).status_code
        == 401
    )
    faux = jwt.encode(
        {"sub": "test@aerosafe.fr", "role": "superviseur"},
        "un-autre-secret-de-test-0123456789abcdef",
        algorithm="HS256",
    )
    rep = client.get("/superviseur", headers={"Authorization": f"Bearer {faux}"})
    assert rep.status_code == 401


def test_jeton_expire(client, monkeypatch):
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "-1")
    assert client.get("/me", headers=jeton(client)).status_code == 401


def test_mot_de_passe_jamais_stocke_en_clair(base):
    with base.moteur.connect() as connexion:
        hashes = connexion.scalars(select(UtilisateurTable.mot_de_passe_hash)).all()
    assert all(h.startswith("$2") for h in hashes)
    assert "motdepasse" not in hashes


def test_adresse_sans_tenir_compte_de_la_casse(client):
    rep = client.post(
        "/login", json={"email": "Test@AeroSafe.fr", "mot_de_passe": "motdepasse"}
    )
    assert rep.status_code == 200


def test_compte_en_double_refuse(base):
    with pytest.raises(CompteExistantError):
        DepotUtilisateurs(base).creer("test@aerosafe.fr", "autre")


def test_role_inconnu_refuse(base):
    with pytest.raises(ValueError, match="Rôle inconnu"):
        DepotUtilisateurs(base).creer("x@aerosafe.fr", "motdepasse", "admin")


def test_creation_de_compte_en_ligne_de_commande(base, client):
    message = CreateurCompte(DepotUtilisateurs(base)).executer(
        ["nouveau@aerosafe.fr", "superviseur"], mot_de_passe="secret123"
    )
    assert message == "Compte créé : nouveau@aerosafe.fr (superviseur)"
    entetes = jeton(client, "nouveau@aerosafe.fr", "secret123")
    assert client.get("/superviseur", headers=entetes).status_code == 200


def test_secret_absent_signale_clairement(monkeypatch):
    monkeypatch.delenv("JWT_SECRET")
    with pytest.raises(ConfigurationManquanteError, match="JWT_SECRET"):
        ServiceAuthentification.creer_token("test@aerosafe.fr", "utilisateur")
