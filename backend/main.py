from datetime import date, datetime
from fastapi import FastAPI, HTTPException, Query

from elexon import fetch_actuals, fetch_forecasts
from metrics import compare_forecasts, calculate_metrics

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title = "Wind Forecast Accuracy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status":"ok",
        "message":"wind forecast api is running"
    }

@app.get("/api/accuracy")
async def get_accuracy(
    delivery_date: date,
    cutoff: datetime = Query(
        description="Forecast decision cutoff, including timezone"
    ),
):
    if cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise HTTPException(
            status_code=400,
            detail="Cutoff must include a timezone, such as Z for UTC",
        )

    try:
        actuals = await fetch_actuals(delivery_date.isoformat())
        forecasts = await fetch_forecasts(
            delivery_date.isoformat(),
            cutoff.isoformat().replace("+00:00", "Z"),
        )

        comparison = compare_forecasts(actuals, forecasts)
        metrics = calculate_metrics(comparison)

        return {
            "deliveryDate": delivery_date.isoformat(),
            "decisionCutoff": cutoff.isoformat(),
            "metrics": metrics,
            "comparison": comparison,
        }

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve or process Elexon data: {exc}",
        )
