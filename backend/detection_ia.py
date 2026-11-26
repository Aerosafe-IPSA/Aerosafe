"""Détection d'anomalies par apprentissage automatique (bonus, issue #37).

Un modèle Isolation Forest est entraîné sur l'historique des positions, sans
données étiquetées. Ses résultats sont comparés aux seuils des règles R1 à R5
du cahier des charges : ``python -m backend.detection_ia``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest
from sqlalchemy import select

from backend.bdd import BaseDeDonnees, ObservationTable


class DonneesInsuffisantesError(Exception):
    """Levée quand l'historique est trop court pour entraîner le modèle."""


@dataclass
class ObservationAnalysee:
    """Une observation et ce qui la distingue de la précédente du même aéronef.

    Les unités sont celles d'OpenSky : mètres, mètres par seconde, degrés et
    secondes. Une valeur absente est remplacée par 0.
    """

    icao24: str
    horodatage: datetime
    altitude: float
    vitesse: float
    taux_vertical: float
    variation_vitesse: float
    variation_cap: float
    silence: float
    age_position: float

    def caracteristiques(self) -> list[float]:
        """Renvoie les valeurs numériques données au modèle."""
        return [
            self.altitude,
            self.vitesse,
            abs(self.taux_vertical),
            self.variation_vitesse,
            self.variation_cap,
            self.silence,
            self.age_position,
        ]

    def regles_depassees(self) -> list[str]:
        """Renvoie les règles R1 à R5 dont le seuil de départ est dépassé.

        Les seuils sont ceux du cahier des charges V3. Cette lecture simplifiée
        sert à la comparaison tant que les alertes ne sont pas enregistrées en
        base (issue #22).
        """
        regles = []
        if self.silence > 300:
            regles.append("R1")
        if self.age_position > 600:
            regles.append("R2")
        if abs(self.taux_vertical) > 15:
            regles.append("R3")
        if self.variation_vitesse > 51:
            regles.append("R4")
        if self.variation_cap > 45:
            regles.append("R5")
        return regles


class LecteurObservations:
    """Lit l'historique en base et prépare les observations pour le modèle."""

    ECART_MAXIMAL = 300.0

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le lecteur.

        Args:
            base: connexion à la base AeroSafe.
        """
        self._moteur = base.moteur

    @staticmethod
    def ecart_angulaire(cap_a: float, cap_b: float) -> float:
        """Renvoie l'écart entre deux caps, ramené entre 0° et 180°."""
        ecart = abs(cap_a - cap_b) % 360
        return 360 - ecart if ecart > 180 else ecart

    @staticmethod
    def _secondes(debut, fin) -> float:
        """Renvoie la durée entre deux dates, ou 0 si l'une est absente."""
        if debut is None or fin is None:
            return 0.0
        return max(0.0, (fin - debut).total_seconds())

    def lire(self) -> list[ObservationAnalysee]:
        """Charge toutes les observations, comparées à la précédente du même aéronef.

        Returns:
            Les observations analysées, par aéronef puis par date.
        """
        requete = select(ObservationTable).order_by(
            ObservationTable.icao24, ObservationTable.observed_at
        )
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete).all()

        observations = []
        precedente = None
        for ligne in lignes:
            variation_vitesse = variation_cap = 0.0
            if precedente is not None and precedente.icao24 == ligne.icao24:
                ecart = self._secondes(precedente.observed_at, ligne.observed_at)
                if 0 < ecart <= self.ECART_MAXIMAL:
                    if ligne.velocity is not None and precedente.velocity is not None:
                        # Variation ramenée à une minute, comme la règle R4
                        variation_vitesse = (
                            abs(ligne.velocity - precedente.velocity) * 60 / ecart
                        )
                    if (
                        ligne.true_track is not None
                        and precedente.true_track is not None
                    ):
                        variation_cap = self.ecart_angulaire(
                            ligne.true_track, precedente.true_track
                        )
            observations.append(
                ObservationAnalysee(
                    icao24=ligne.icao24,
                    horodatage=ligne.observed_at,
                    altitude=ligne.baro_altitude or 0.0,
                    vitesse=ligne.velocity or 0.0,
                    taux_vertical=ligne.vertical_rate or 0.0,
                    variation_vitesse=variation_vitesse,
                    variation_cap=variation_cap,
                    silence=self._secondes(ligne.last_contact, ligne.observed_at),
                    age_position=self._secondes(ligne.time_position, ligne.observed_at),
                )
            )
            precedente = ligne
        return observations


class DetecteurAnomaliesIA:
    """Modèle Isolation Forest qui attribue un score d'anomalie à chaque observation.

    Le score va de 0 (vol ordinaire) à 1 (vol très atypique). Le modèle apprend
    seul ce qu'est un vol ordinaire : il n'a pas besoin d'exemples d'anomalies.
    """

    MINIMUM_OBSERVATIONS = 50

    def __init__(self, contamination: float = 0.01, graine: int = 42) -> None:
        """Prépare le modèle.

        Args:
            contamination: part des observations considérées comme atypiques.
            graine: valeur qui rend l'entraînement reproductible.
        """
        self._modele = IsolationForest(
            n_estimators=100, contamination=contamination, random_state=graine
        )
        self._entraine = False

    def entrainer(self, observations: list[ObservationAnalysee]) -> None:
        """Entraîne le modèle sur l'historique.

        Args:
            observations: observations lues en base.

        Raises:
            DonneesInsuffisantesError: moins de 50 observations disponibles.
        """
        if len(observations) < self.MINIMUM_OBSERVATIONS:
            raise DonneesInsuffisantesError(
                f"{len(observations)} observations en base : il en faut au moins "
                f"{self.MINIMUM_OBSERVATIONS} pour entraîner le modèle"
            )
        self._modele.fit([o.caracteristiques() for o in observations])
        self._entraine = True

    def scores(self, observations: list[ObservationAnalysee]) -> list[float]:
        """Renvoie le score d'anomalie de chaque observation, entre 0 et 1."""
        self._verifier_entrainement()
        valeurs = self._modele.score_samples(
            [o.caracteristiques() for o in observations]
        )
        return [float(-valeur) for valeur in valeurs]

    def anomalies(self, observations: list[ObservationAnalysee]) -> list[bool]:
        """Indique, pour chaque observation, si le modèle la juge atypique."""
        self._verifier_entrainement()
        verdicts = self._modele.predict([o.caracteristiques() for o in observations])
        return [bool(verdict == -1) for verdict in verdicts]

    def _verifier_entrainement(self) -> None:
        """Refuse de prédire tant que le modèle n'a pas été entraîné."""
        if not self._entraine:
            raise RuntimeError("Le modèle doit être entraîné avant de prédire")


@dataclass
class ComparaisonReglesIA:
    """Bilan de la comparaison entre les règles R1 à R5 et le modèle."""

    total: int
    regles_et_ia: int
    regles_seules: int
    ia_seule: int

    @property
    def aucune(self) -> int:
        """Nombre d'observations jugées normales par les deux approches."""
        return self.total - self.regles_et_ia - self.regles_seules - self.ia_seule

    @property
    def taux_accord(self) -> float:
        """Part des observations sur lesquelles les deux approches sont d'accord."""
        if self.total == 0:
            return 0.0
        return (self.regles_et_ia + self.aucune) / self.total

    @property
    def part_des_regles_retrouvee(self) -> float:
        """Part des dépassements de seuil que le modèle signale aussi."""
        signalees = self.regles_et_ia + self.regles_seules
        return self.regles_et_ia / signalees if signalees else 0.0

    def resume(self) -> str:
        """Renvoie le bilan sous forme de texte lisible."""
        return "\n".join(
            [
                f"Observations analysées          : {self.total}",
                f"Signalées par les règles et l'IA : {self.regles_et_ia}",
                f"Signalées par les règles seules  : {self.regles_seules}",
                f"Signalées par l'IA seule         : {self.ia_seule}",
                f"Jugées normales par les deux     : {self.aucune}",
                f"Taux d'accord                    : {self.taux_accord:.1%}",
                f"Dépassements retrouvés par l'IA  : {self.part_des_regles_retrouvee:.1%}",
            ]
        )


class AnalyseIA:
    """Entraîne le modèle sur la base et compare ses résultats aux règles."""

    def __init__(
        self, base: BaseDeDonnees, detecteur: DetecteurAnomaliesIA | None = None
    ) -> None:
        """Prépare l'analyse.

        Args:
            base: connexion à la base AeroSafe.
            detecteur: modèle à utiliser ; un modèle par défaut sinon.
        """
        self._lecteur = LecteurObservations(base)
        self._detecteur = detecteur or DetecteurAnomaliesIA()
        self._observations: list[ObservationAnalysee] | None = None

    def _preparer(self) -> list[ObservationAnalysee]:
        """Lit l'historique et entraîne le modèle, une seule fois."""
        if self._observations is None:
            observations = self._lecteur.lire()
            self._detecteur.entrainer(observations)
            self._observations = observations
        return self._observations

    def comparer(self) -> ComparaisonReglesIA:
        """Entraîne le modèle puis le compare aux seuils des règles.

        Returns:
            Le bilan de la comparaison.
        """
        observations = self._preparer()
        verdicts = self._detecteur.anomalies(observations)
        bilan = ComparaisonReglesIA(len(observations), 0, 0, 0)
        for observation, atypique in zip(observations, verdicts):
            par_regle = bool(observation.regles_depassees())
            if par_regle and atypique:
                bilan.regles_et_ia += 1
            elif par_regle:
                bilan.regles_seules += 1
            elif atypique:
                bilan.ia_seule += 1
        return bilan

    def plus_atypiques(
        self, nombre: int = 10
    ) -> list[tuple[ObservationAnalysee, float]]:
        """Renvoie les observations au score d'anomalie le plus élevé.

        Args:
            nombre: nombre d'observations à renvoyer.

        Returns:
            Des couples (observation, score), du plus atypique au moins atypique.
        """
        observations = self._preparer()
        scores = self._detecteur.scores(observations)
        classement = sorted(zip(observations, scores), key=lambda c: c[1], reverse=True)
        return classement[:nombre]


def main() -> None:
    """Affiche la comparaison et les dix observations les plus atypiques."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    journal = logging.getLogger("ia")
    analyse = AnalyseIA(BaseDeDonnees())
    try:
        journal.info(analyse.comparer().resume())
        journal.info("\nObservations les plus atypiques :")
        for observation, score in analyse.plus_atypiques():
            regles = ", ".join(observation.regles_depassees()) or "aucune règle"
            journal.info(
                "  %s  %s  score %.2f  (%s)",
                observation.icao24,
                observation.horodatage,
                score,
                regles,
            )
    except DonneesInsuffisantesError as erreur:
        journal.error("Analyse impossible : %s", erreur)


if __name__ == "__main__":
    main()
