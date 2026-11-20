"""
Connexion à la base de donnée PostgreSQL via SQLAlchemy.
Fournit le moteur, la session et la classe de base pour les modèles ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# Charge les variables d'environement depuis le fichier .env à la racine du projet
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# On remplace postgresql:// par postgresql+psycopg2:// pour forcer l'utilisation du bon driver
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)

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
