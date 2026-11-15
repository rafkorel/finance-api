from datetime import date as DateType
from decimal import Decimal

from fastapi import HTTPException
import pytest

from app.integrations.cbr import parse_cbr_rates_xml

@pytest.fixture
def cbr_xml():

    xml_data = """
    <ValCurs Date="13.11.2026">
        <Valute ID="R01235">
            <CharCode>USD</CharCode>
            <Nominal>10</Nominal>
            <Value>802,50</Value>
        </Valute>

        <Valute ID="R01239">
            <CharCode>EUR</CharCode>
            <Nominal>1</Nominal>
            <Value>100,50</Value>
        </Valute>
    </ValCurs>
    """

    return xml_data


def test_parse_cbr_rates_xml_returns_date_and_rates(cbr_xml):

    date, rates = parse_cbr_rates_xml(cbr_xml)

    assert date == DateType(2026, 11, 13)
    assert rates["USD"] == Decimal("80.25")
    assert rates["EUR"] == Decimal("100.5")


def test_parse_cbr_rates_xml_missing_eur(cbr_xml):

    cbr_xml = cbr_xml.replace("EUR", "GBP")

    with pytest.raises(HTTPException) as exc_info:

        parse_cbr_rates_xml(cbr_xml)

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == 'CBR response does not contain required currencies'