"""Connexion à PostgreSQL et tables de l'historique des vols.

Les tables suivent le modèle de données du cahier des charges V3 :
``aircraft`` (un aéronef), ``observation`` (une position reçue à un instant) et
``app_user`` (un compte).
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


class BaseInjoignableError(Exception):
    """Levée quand la base de données ne répond pas à l'ouverture de la connexion."""


class Base(DeclarativeBase):
    """Classe mère de toutes les tables de la base AeroSafe."""


class AircraftTable(Base):
    """Table ``aircraft`` : un aéronef, identifié par son adresse ICAO24."""

    __tablename__ = "aircraft"

    icao24: Mapped[str] = mapped_column(String(6), primary_key=True)
    callsign: Mapped[Optional[str]] = mapped_column(String(8))
    origin_country: Mapped[Optional[str]] = mapped_column(String(64))
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ObservationTable(Base):
    """Table ``observation`` : une position d'un aéronef reçue à un instant donné.

    L'index unique sur (icao24, observed_at) accélère la reconstruction des
    trajets et empêche d'enregistrer deux fois la même observation.
    """

    __tablename__ = "observation"
    __table_args__ = (
        Index(
            "ix_observation_icao24_observed_at", "icao24", "observed_at", unique=True
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    icao24: Mapped[str] = mapped_column(String(6), ForeignKey("aircraft.icao24"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    baro_altitude: Mapped[Optional[float]] = mapped_column(Float)
    velocity: Mapped[Optional[float]] = mapped_column(Float)
    true_track: Mapped[Optional[float]] = mapped_column(Float)
    vertical_rate: Mapped[Optional[float]] = mapped_column(Float)
    on_ground: Mapped[bool] = mapped_column(Boolean, default=False)
    last_contact: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    time_position: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class UtilisateurTable(Base):
    """Table ``app_user`` : un compte de l'application et son rôle.

    Le mot de passe n'est jamais stocké en clair, seulement son hash bcrypt.
    """

    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16), default="utilisateur")


class BaseDeDonnees:
    """Connexion à la base AeroSafe : PostgreSQL en production, SQLite pour les tests."""

    def __init__(self, url: Optional[str] = None) -> None:
        """Ouvre la connexion et crée les tables si elles n'existent pas.

        Args:
            url: adresse SQLAlchemy de la base ; par défaut celle du fichier .env.

        Raises:
            BaseInjoignableError: la base ne répond pas.
        """
        self._url = url or self.url_depuis_env()
        options = {}
        if self._url.startswith("sqlite"):
            # Base de test en mémoire : une seule connexion, partagée entre les fils
            options = {
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            }
        elif self._url.startswith("postgresql"):
            # Toutes les dates sont lues et écrites en UTC (cahier des charges V3)
            options = {"connect_args": {"options": "-c timezone=utc"}}
        self._moteur = create_engine(self._url, **options)
        try:
            Base.metadata.create_all(self._moteur)
        except OperationalError as erreur:
            raise BaseInjoignableError(
                "Base de données injoignable. Vérifie que Docker est démarré, lance "
                "`docker compose up -d`, puis contrôle les variables POSTGRES_* du "
                "fichier .env."
            ) from erreur

    @property
    def moteur(self) -> Engine:
        """Moteur SQLAlchemy, utilisé par les dépôts pour lire et écrire."""
        return self._moteur

    @staticmethod
    def url_depuis_env() -> str:
        """Construit l'adresse de la base à partir des variables du fichier .env.

        ``DATABASE_URL`` est utilisée telle quelle si elle existe ; sinon l'adresse
        est construite avec les variables ``POSTGRES_*`` déjà utilisées par
        docker-compose.
        """
        if os.getenv("DATABASE_URL"):
            return os.environ["DATABASE_URL"]
        utilisateur = os.getenv("POSTGRES_USER", "aerosafe")
        mot_de_passe = os.getenv("POSTGRES_PASSWORD", "")
        hote = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        base = os.getenv("POSTGRES_DB", "aerosafe")
        return f"postgresql+psycopg://{utilisateur}:{mot_de_passe}@{hote}:{port}/{base}"
