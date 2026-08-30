from decimal import Decimal

from app.utils.money import compute_totals


def test_compute_totals_no_tax():
    subtotal, total = compute_totals([(Decimal(2), 1000), (Decimal(1), 500)], Decimal(0))
    assert subtotal == 2500
    assert total == 2500


def test_compute_totals_with_tax():
    # 100.00€ HT + 20% de TVA = 120.00€ TTC
    subtotal, total = compute_totals([(Decimal(1), 10000)], Decimal(20))
    assert subtotal == 10000
    assert total == 12000


def test_compute_totals_rounds_half_up():
    # 3 x 333 = 999 cents de subtotal ; TVA 5.5% de 999 = 54.945 -> arrondi à 55
    subtotal, total = compute_totals([(Decimal(3), 333)], Decimal("5.5"))
    assert subtotal == 999
    assert total == 1054


def test_compute_totals_fractional_quantity():
    # Quantité non entière (ex : 2.5 heures facturées)
    subtotal, total = compute_totals([(Decimal("2.5"), 4000)], Decimal(0))
    assert subtotal == 10000
    assert total == 10000


def test_compute_totals_empty_line_items():
    subtotal, total = compute_totals([], Decimal(20))
    assert subtotal == 0
    assert total == 0
