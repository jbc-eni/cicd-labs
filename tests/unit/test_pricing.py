"""Tests unitaires des règles de prix — POINT DE DÉPART (Atelier 1).

Complétez ce fichier : objectif >= 90 % de couverture sur minishop/pricing.py.
"""

from decimal import Decimal

import pytest

from minishop.pricing import coupon_discount, line_total, money, quote, shipping_cost


def test_money_arrondi_commercial():
    """0.125 s'arrondit à 0.13 (ROUND_HALF_UP), pas 0.12."""
    assert money("0.125") == Decimal("0.13")

pytestmark = pytest.mark.unit

def test_line_total_sans_remise():
    assert line_total(Decimal("12.50"), 2) == Decimal("25.00")


def test_quote_panier_vide():
    """Un panier vide coûte 0 € : pas de frais de livraison."""
    q = quote([])
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")


# TODO Atelier 1 :
#  - remise volume à partir de 10 unités (et pas à 9 !)
#  - quantités invalides (0, 100, -1, "2", True) -> ValueError   (astuce : @pytest.mark.parametrize)
#  - coupons WELCOME10 / FIXED5 / FREESHIP (seuils inclus/exclus), coupon inconnu, casse
#  - livraison offerte à partir de 50 € APRÈS remise
#  - produit inconnu -> KeyError

def test_line_total_avec_remise():
    assert line_total(Decimal("2.50"), 9) == Decimal("22.50")
    assert line_total(Decimal("2.50"), 10) == Decimal("25.00") * (1 - Decimal("0.05"))


@pytest.mark.parametrize("quantite", [0, 100, -1, "2", True])
def test_line_total_quantites_invalides(quantite):
    with pytest.raises(ValueError):
        line_total(Decimal("2.50"), quantite)


@pytest.mark.parametrize("subtotal, coupon, resultat", [
    # WELCOME10
    (Decimal("19.99"), "WELCOME10", Decimal("0.00")),
    (Decimal("20.00"), "WELCOME10", Decimal("2.00")),
    (Decimal("30.00"), "WELCOME10", Decimal("3.00")),

    # FIXED5
    (Decimal("29.99"), "FIXED5", Decimal("0.00")),
    (Decimal("30.00"), "FIXED5", Decimal("5.00")),
    (Decimal("40.00"), "FIXED5", Decimal("5.00")),

    # FREESHIP
    (Decimal("50.00"), "FREESHIP", Decimal("0.00")),
])
def test_coupon_discount(subtotal, coupon, resultat):
    assert coupon_discount(subtotal, coupon) == resultat


def test_coupon_inconnu():
    with pytest.raises(ValueError):
        coupon_discount(Decimal("50.00"), "INVALID")


@pytest.mark.parametrize("coupon", [
    "welcome10",
    "Welcome10",
    "WELCOME10",
    "  welcome10  ",
])
def test_coupon_casse(coupon):
    assert coupon_discount(Decimal("20.00"), coupon) == Decimal("2.00")


@pytest.mark.parametrize("montant, resultat", [
    (Decimal("49.99"), Decimal("4.90")),
    (Decimal("50.00"), Decimal("0.00")),
    (Decimal("50.01"), Decimal("0.00")),
])
def test_frais_livraison_seuil(montant, resultat):
    assert shipping_cost(montant, None, empty=False) == resultat


def test_livraison_gratuite_coupon():
    assert shipping_cost(
        Decimal("10.00"), "FREESHIP", empty=False
    ) == Decimal("0.00")


def test_panier_vide_sans_livraison():
    assert shipping_cost(
        Decimal("0.00"), None, empty=True
    ) == Decimal("0.00")


def test_produit_inconnu():
    with pytest.raises(KeyError):
        quote([{"product_id": "PRODUIT_INCONNU", "qty": 1}])


########### ATELIER 1 - TDD #####################


@pytest.mark.parametrize("items, resultat", [
    # Cas 1 : remise de 15 % sans minimum
    ([{"product_id": "sticker", "qty": 1}], Decimal("0.37")),
    # Cas 2 : remise de 15 % sur une ligne sans remise volume
    ([{"product_id": "sticker", "qty": 2}], Decimal("0.74")),
    # Cas 3 : aucune remise STUDENT15 sur une ligne bénéficiant
    # déjà de la remise volume
    ([{"product_id": "sticker", "qty": 10}], Decimal("0.00")),
])
def test_coupon_student15(items, resultat):
    result = quote(items, coupon="STUDENT15")
    assert result.discount == resultat

