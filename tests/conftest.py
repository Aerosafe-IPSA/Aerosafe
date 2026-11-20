"""
Configuration globale des tests.
Ce fichier est chargé en premier par pytest — on y définit les variables
d'environnement nécessaires avant que les modules backend soient importés.
"""

import os

# Valeur factice utilisée uniquement pendant les tests
os.environ.setdefault("JWT_SECRET", "secret-de-test-pour-pytest")
