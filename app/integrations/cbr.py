from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError, TimeoutException
import xml.etree.ElementTree as ET


async def fetch_cbr_rates_xml() -> str:

    url = "https://www.cbr.ru/scripts/XML_daily.asp"

    try:
        async with AsyncClient(timeout=10.0) as client:

            response = await client.get(url)

            response.raise_for_status()

        return response.text

    except TimeoutException:

        raise HTTPException(
            status_code=504,
            detail="The timeout for a response from the CBR server has been exceeded"
        )

    except RequestError:

        raise HTTPException(
            status_code=503,
            detail="CBR Server Response Error"
        )

    except HTTPStatusError:

        raise HTTPException(
            status_code=502,
            detail="CBR Server Status Error"
        )


def parse_cbr_rates_xml(xml_data: str) -> tuple[date, dict[str, Decimal]]:

    try:
        root = ET.fromstring(xml_data)

        date = root.get("Date")
        if not date:
            raise HTTPException(
                status_code=502,
                detail="CBR response does not contain a valid rate date"
            )
        date = datetime.strptime(
            date,
            "%d.%m.%Y"
        ).date()

        currencies = root.findall("Valute")
        if not currencies:
            raise HTTPException(
                status_code=502,
                detail="CBR response does not contain currencies"
            )

        rates = {}

        for currency in currencies:

            charcode = currency.findtext("CharCode")
            if charcode not in ("USD", "EUR"):
                continue

            nominal = currency.findtext("Nominal")
            if not nominal:
                raise HTTPException(
                    status_code=502,
                    detail="The 'nominal' field is missing"
                )
            nominal = nominal.replace(",", ".")
            nominal = Decimal(nominal)
            if not nominal.is_finite():
                raise HTTPException(
                    status_code=502,
                    detail="The value 'nominal' cannot be used"
                )
            if nominal <= 0:
                raise HTTPException(
                    status_code=502,
                    detail="The nominal value is less than or equal to 0"
                )

            value = currency.findtext("Value")
            if not value:
                raise HTTPException(
                    status_code=502,
                    detail="The 'value' field is missing"
                )
            value = value.replace(",", ".")
            value = Decimal(value)
            if not value.is_finite():
                raise HTTPException(
                    status_code=502,
                    detail="The value 'value' cannot be used"
                )
            if value <= 0:
                raise HTTPException(
                    status_code=502,
                    detail="The value is less than or equal to 0"
                )

            one_value = value / nominal
            rates[charcode] = one_value


        if "USD" not in rates or "EUR" not in rates:
            raise HTTPException(
                status_code=502,
                detail="CBR response does not contain required currencies"
            )

        return (date, rates)

    except ET.ParseError:

        raise HTTPException(
            status_code=502,
            detail="XML parsing error"
        )

    except InvalidOperation:

        raise HTTPException(
            status_code=502,
            detail="An invalid number was received for conversion"
        )

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail="Invalid Date value"
        )