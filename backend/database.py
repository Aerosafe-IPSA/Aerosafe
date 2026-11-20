"""
Connexion à la base de donnée PostgreSQL via SQLAlchemy.
Fournit le moteur, la session et la classe de base pour les modèles ORM.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charge les variables d'environement depuis le fichier .env à la racine du projet
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Fallback SQLite pour la CI (pas de Postgres disponible)
_url = os.getenv("DATABASE_URL", "")
if _url:
    DATABASE_URL = _url.replace("postgresql://", "postgresql+psycopg2://")
else:
    DATABASE_URL = "sqlite:///./aerosafe_test.db"

_kwargs = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_kwargs)

# autocommit=False : on valide manuellement les transactions (db.commit())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base dont héritent tous les modèles ORM
Base = declarative_base()


def get_db():
    """Générateur de session injecté par FastAPI dans chaque route via Depends()."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # On ferme toujours la session même en cas d'erreur
        db.close()
