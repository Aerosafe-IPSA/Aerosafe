from sqlalchemy import Column, Integer, String
from backend.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="utilisateur")    