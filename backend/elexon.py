
from datetime import datetime, timezone ,timedelta

import httpx

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


async def fetch_actuals(delivery_date: str):
    url = f"{BASE_URL}/FUELHH/stream"

    params = {
        "settlementDateFrom": delivery_date,
        "settlementDateTo": delivery_date,
        "fuelType": "WIND",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_forecasts(
    delivery_date: str,
    cutoff: str,
    lookback_hours: int = 48,
):
    cutoff_dt = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))

    if cutoff_dt.tzinfo is None:
        raise ValueError("Cutoff must include a timezone")

    cutoff_dt = cutoff_dt.astimezone(timezone.utc)
    publish_from = cutoff_dt - timedelta(hours=lookback_hours)

    url = f"{BASE_URL}/WINDFOR/stream"
    params = {
        "publishDateTimeFrom": publish_from.isoformat().replace("+00:00", "Z"),
        "publishDateTimeTo": cutoff_dt.isoformat().replace("+00:00", "Z"),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records = response.json()

    eligible = [
        record
        for record in records
        if record["startTime"].startswith(delivery_date)
        and datetime.fromisoformat(
            record["publishTime"].replace("Z", "+00:00")
        ) <= cutoff_dt
    ]

    latest_by_start = {}

    for record in eligible:
        start_time = record["startTime"]
        existing = latest_by_start.get(start_time)

        if (
            existing is None
            or record["publishTime"] > existing["publishTime"]
        ):
            latest_by_start[start_time] = record

    return sorted(
        latest_by_start.values(),
        key=lambda record: record["startTime"],
    )