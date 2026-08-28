from decimal import ROUND_HALF_UP, Decimal


def compute_totals(line_items: list[tuple[Decimal, int]], tax_rate: Decimal) -> tuple[int, int]:
    """line_items = [(quantity, unit_price_cents), ...]. Retourne
    (subtotal_cents, total_cents). Tout en Decimal jusqu'à l'arrondi final —
    jamais de float sur de l'argent, jamais un total calculé côté client
    (le serveur recalcule toujours, pour ne jamais faire confiance à un
    total envoyé par le navigateur)."""
    subtotal = sum((qty * price for qty, price in line_items), Decimal(0))
    subtotal_cents = int(subtotal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    tax_amount = Decimal(subtotal_cents) * tax_rate / Decimal(100)
    total_cents = subtotal_cents + int(tax_amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    return subtotal_cents, total_cents
