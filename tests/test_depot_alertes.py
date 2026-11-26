"""Tests de l'enregistrement des alertes et de la détection pendant la collecte."""

from datetime import datetime, timedelta, timezone

import pytest

from backend.bdd import BaseDeDonnees
from backend.depot_alertes import DepotAlertes
from backend.rules.alerte import Alerte
from backend.rules.moteur import MoteurRegles
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol
from collector.rejeu import RejeuHistorique
from collector.service import ServiceCollecte

T0 = datetime(2026, 11, 26, 14, 32, tzinfo=timezone.utc)


def aeronef(minute, cap=200.0, taux_vertical=-0.3, icao24="39bd24"):
    """Fabrique un aéronef avec un seul état, reçu à T0 + minute."""
    instant = int(T0.timestamp()) + 60 * minute
    ligne = [
        icao24,
        "AFR1462",
        "France",
        instant - 2,
        instant - 1,
        1.44,
        43.63,
        9144.0,
        False,
        228.0,
        cap,
        taux_vertical,
        None,
        9200.0,
        "1000",
        False,
        0,
    ]
    avion = Aeronef(icao24, "AFR1462", "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(ligne, instant))
    return avion


def alerte(regle="R3", minutes=0, icao24="39bd24"):
    """Fabrique une alerte comme le ferait le moteur de règles."""
    return Alerte(
        icao24, regle, T0 + timedelta(minutes=minutes), 18.4, 15.0, f"Alerte {regle}"
    )


class FauxCollecteur:
    """Collecteur de test : renvoie à chaque cycle le même aéronef, cap imposé."""

    def __init__(self, caps):
        """Garde la liste des caps à renvoyer, un par cycle."""
        self._caps = list(caps)
        self._cycle = 0

    def recuperer_etats(self):
        """Renvoie l'aéronef du cycle courant, comme le vrai collecteur."""
        avion = aeronef(self._cycle, cap=self._caps[self._cycle])
        self._cycle += 1
        return [avion]


@pytest.fixture
def base():
    """Base de test contenant l'aéronef 39bd24."""
    base = BaseDeDonnees("sqlite://")
    DepotPositions(base).enregistrer([aeronef(0), aeronef(0, icao24="4ca7b3")])
    return base


def test_alerte_enregistree_puis_relue(base):
    depot = DepotAlertes(base)

    assert depot.enregistrer([alerte()]) == 1

    relues = depot.lister()
    assert len(relues) == 1
    assert relues[0].icao24 == "39bd24"
    assert relues[0].callsign == "AFR1462"
    assert relues[0].nom_regle == "R3"
    assert relues[0].valeur_observee == 18.4
    assert relues[0].seuil == 15.0
    assert relues[0].statut == "en cours"


def test_meme_regle_meme_aeronef_dans_les_dix_minutes_ignoree(base):
    depot = DepotAlertes(base)
    depot.enregistrer([alerte(minutes=0)])

    assert depot.existe_deja(alerte(minutes=2)) is True
    assert depot.enregistrer([alerte(minutes=2)]) == 0
    assert len(depot.lister()) == 1


def test_doublons_ignores_dans_un_meme_lot(base):
    depot = DepotAlertes(base)

    assert depot.enregistrer([alerte(minutes=1), alerte(minutes=0)]) == 1


def test_alerte_enregistree_apres_dix_minutes(base):
    depot = DepotAlertes(base)
    depot.enregistrer([alerte(minutes=0)])

    assert depot.existe_deja(alerte(minutes=11)) is False
    assert depot.enregistrer([alerte(minutes=11)]) == 1


def test_autre_regle_ou_autre_aeronef_enregistree(base):
    depot = DepotAlertes(base)
    depot.enregistrer([alerte("R3")])

    assert depot.enregistrer([alerte("R5"), alerte("R3", icao24="4ca7b3")]) == 2
    assert len(depot.lister("39BD24")) == 2


def test_liste_vide_sans_rien_enregistrer(base):
    assert DepotAlertes(base).enregistrer([]) == 0


def test_detection_pendant_la_collecte():
    base = BaseDeDonnees("sqlite://")
    alertes = DepotAlertes(base)
    # Caps successifs : 350° -> 10° (20° d'écart), 10° -> 100° (90°), 100° -> 200°
    service = ServiceCollecte(
        FauxCollecteur([350.0, 10.0, 100.0, 200.0]),
        DepotPositions(base),
        moteur=MoteurRegles(),
        depot_alertes=alertes,
    )

    service.executer_cycle()
    service.executer_cycle()
    assert alertes.lister() == []

    service.executer_cycle()
    assert [a.nom_regle for a in alertes.lister()] == ["R5"]
    assert alertes.lister()[0].valeur_observee == 90.0

    # Le nouveau virage arrive moins de dix minutes après : pas de doublon
    service.executer_cycle()
    assert len(alertes.lister()) == 1


def test_collecte_sans_moteur_ne_detecte_rien():
    base = BaseDeDonnees("sqlite://")
    service = ServiceCollecte(FauxCollecteur([10.0, 100.0]), DepotPositions(base))

    assert service.executer_cycle() == 1
    assert service.executer_cycle() == 1
    assert DepotAlertes(base).lister() == []


def test_rejeu_de_l_historique():
    base = BaseDeDonnees("sqlite://")
    positions = DepotPositions(base)
    for minute, cap in enumerate([10.0, 100.0, 100.0]):
        positions.enregistrer([aeronef(minute, cap=cap)])
    positions.enregistrer([aeronef(3, taux_vertical=-18.4, icao24="4ca7b3")])
    depot = DepotAlertes(base)
    rejeu = RejeuHistorique(base, MoteurRegles(), depot)

    assert rejeu.rejouer() == 2
    assert {(a.icao24, a.nom_regle) for a in depot.lister()} == {
        ("39bd24", "R5"),
        ("4ca7b3", "R3"),
    }
    # Un second rejeu ne crée aucun doublon
    assert rejeu.rejouer() == 0
