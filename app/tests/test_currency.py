from decimal import Decimal

import pytest

from app.service.currency import convert_currency

def test_convert_currency_usd_to_eur():

    amount = Decimal("10")
    from_currency = "USD"
    to_currency = "EUR"
    rates = {
        "USD": Decimal("80"),
        "EUR": Decimal("100"),
    }

    result, exchange_rate = convert_currency(amount, from_currency, to_currency, rates)

    assert result == Decimal("8") and exchange_rate == Decimal("0.8")


@pytest.mark.parametrize(
        "amount, expected",
        [
            (Decimal("100.49"), Decimal("1")),
            (Decimal("100.5"), Decimal("1.01")),
            (Decimal("100.51"), Decimal("1.01"))
        ],
)
def test_convert_currency_rounds_half_up(amount, expected):

    from_currency = "RUB"
    to_currency = "USD"
    rates = {
        "RUB": Decimal("1"),
        "USD": Decimal("100"),
    }

    result = convert_currency(amount, from_currency, to_currency, rates)[0]

    assert result == expected


def test_convert_currency_rejects_missing_target_rate():

    amount = Decimal("10")
    from_currency = "USD"
    to_currency = "EUR"
    rates = {
        "USD": Decimal("80"),
    }

    with pytest.raises(ValueError):

        convert_currency(amount, from_currency, to_currency, rates)


