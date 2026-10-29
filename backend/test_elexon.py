
import asyncio
from elexon import fetch_actuals, fetch_forecasts


async def main():
    delivery_date = "2026-01-15"
    cutoff = "2026-01-14T12:00:00Z"

    actuals = await fetch_actuals(delivery_date)
    forecasts = await fetch_forecasts(delivery_date, cutoff)

    print("Actual records:", len(actuals))
    print("Selected forecasts:", len(forecasts))
    print("First forecast:", forecasts[0] if forecasts else None)


asyncio.run(main())
