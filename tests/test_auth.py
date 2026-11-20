"""
Tests d'intégration pour les routes d'authentification (/login, /me, /superviseur).
On utilise TestClient (FastAPI) avec une base SQLite en mémoire pour ne pas
dépendre d'un Postgres local ou CI.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import Utilisateur
from backend.security import ServiceAuthentification

# StaticPool : toutes les connexions partagent la même base en mémoire
_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


@pytest.fixture(autouse=True)
def db_propre():
    """Recrée les tables et insère un utilisateur de test avant chaque test."""
    Base.metadata.create_all(bind=_ENGINE)
    db = _SessionTest()
    db.add(
        Utilisateur(
            email="test@aerosafe.fr",
            mot_de_passe_hash=ServiceAuthentification.hasher_mot_de_passe("motdepasse"),
            role="utilisateur",
        )
    )
    db.add(
        Utilisateur(
            email="superviseur@aerosafe.fr",
            mot_de_passe_hash=ServiceAuthentification.hasher_mot_de_passe("superpass"),
            role="superviseur",
        )
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=_ENGINE)


@pytest.fixture
def client():
    """TestClient avec la base SQLite injectée à la place de la vraie base."""
    def _get_db_test():
        db = _SessionTest()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db_test
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_connexion_reussie(client):
    rep = client.post("/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "motdepasse"})
    assert rep.status_code == 200
    assert "access_token" in rep.json()
    assert rep.json()["token_type"] == "bearer"


def test_mauvais_mot_de_passe(client):
    rep = client.post("/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "mauvais"})
    assert rep.status_code == 401


def test_acces_superviseur_refuse_a_utilisateur(client):
    # D'abord on récupère un token utilisateur normal
    login = client.post("/login", json={"email": "test@aerosafe.fr", "mot_de_passe": "motdepasse"})
    token = login.json()["access_token"]

    rep = client.get("/superviseur", headers={"Authorization": f"Bearer {token}"})
    assert rep.status_code == 403
