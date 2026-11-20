"""
Modèles ORM SQLAlchemy — définissent la structure des tables en base de données.
"""

from sqlalchemy import Column, Integer, String
from backend.database import Base


class Utilisateur(Base):
    """Représente un utilisateur de l'application AeroSafe."""

    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # On ne stocke jamais le mot de passe en clair, uniquement le hash bcrypt
    mot_de_passe_hash = Column(String, nullable=False)

    # Deux roles possibles : "utilisateur" ou "superviseur"
    role = Column(String, nullable=False, default="utilisateur")
