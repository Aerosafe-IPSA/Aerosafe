"""Point d'entrée de l'API : ``uvicorn backend.main:app --reload``."""

from dotenv import load_dotenv

from backend.application import ApplicationAeroSafe

load_dotenv()
app = ApplicationAeroSafe().app
