"""Écart entre deux caps, pour la règle R5."""


def ecart_angulaire(cap_a: float, cap_b: float) -> float:
    """Renvoie l'écart entre deux caps, ramené entre 0° et 180°.

    Passer de 350° à 10° représente 20° d'écart, et non 340°.
    """
    ecart = abs(cap_a - cap_b) % 360
    return 360 - ecart if ecart > 180 else ecart
