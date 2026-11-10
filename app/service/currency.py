from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.integrations.cbr import (
    fetch_cbr_rates_xml,
    parse_cbr_rates_xml
)

def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rates: dict[str, Decimal]
) -> tuple[Decimal, Decimal]:

    if not amount.is_finite():
        raise ValueError("The value 'amount' cannot be used")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if from_currency not in rates or to_currency not in rates:
        raise ValueError("Invalid Currencies")
    
    if not rates[from_currency].is_finite():
        raise ValueError("Invalid source currency exchange rate")
    if rates[from_currency] <= 0:
        raise ValueError("The value 'from_currency' is less than or equal to 0")

    if not rates[to_currency].is_finite():
        raise ValueError("Invalid target currency exchange rate")
    if rates[to_currency] <= 0:
        raise ValueError("The value 'to_currency' is less than or equal to 0")

    exchange_rate = rates[from_currency] / rates[to_currency]
    result = amount * rates[from_currency] / rates[to_currency]

    result_round = result.quantize(
        Decimal("0.01"),
        ROUND_HALF_UP
    )
    if result_round <= 0:
        raise ValueError("Result must be greater than zero")

    return (result_round, exchange_rate)


async def convert_with_cbr(
    amount: Decimal,
    from_currency: str,
    to_currency: str
) -> tuple[Decimal, Decimal, date | None]:

    correct_rates = {"USD", "EUR", "RUB"}
    if from_currency not in correct_rates or to_currency not in correct_rates:
        raise ValueError("Invalid Currencies")

    if not amount.is_finite():
        raise ValueError("The value 'amount' cannot be used")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if from_currency == to_currency:

        result, exchange_rate = convert_currency(amount, from_currency, to_currency, {from_currency: Decimal("1")})
        return (result, exchange_rate, None)

    data = await fetch_cbr_rates_xml()

    rate_date, rates = parse_cbr_rates_xml(data)
    rates["RUB"] = Decimal("1")

    result, exchange_rate = convert_currency(amount, from_currency, to_currency, rates)

    return (result, exchange_rate, rate_date)