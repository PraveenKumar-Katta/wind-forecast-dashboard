
import math


def compare_forecasts(actuals, forecasts):
    actual_by_time = {
        record["startTime"]: record
        for record in actuals
    }

    comparison = []

    for forecast in forecasts:
        start_time = forecast["startTime"]
        actual = actual_by_time.get(start_time)

        comparison.append({
            "startTime": start_time,
            "publishTime": forecast["publishTime"],
            "forecastGeneration": forecast["generation"],
            "actualGeneration": (
                actual["generation"] if actual else None
            ),
            "error": (
                actual["generation"] - forecast["generation"]
                if actual else None
            ),
        })

    return comparison



def calculate_metrics(comparison):
    valid = [
        row for row in comparison
        if row["actualGeneration"] is not None
        and row["forecastGeneration"] is not None
    ]

    missing_actuals = sum(
        row["actualGeneration"] is None
        for row in comparison
    )

    missing_forecasts = sum(
        row["forecastGeneration"] is None
        for row in comparison
    )

    if not valid:
        raise ValueError(
            "No matched forecast and actual records"
        )

    errors = [row["error"] for row in valid]

    mae = sum(abs(error) for error in errors) / len(errors)

    rmse = math.sqrt(
        sum(error ** 2 for error in errors) / len(errors)
    )

    bias = sum(errors) / len(errors)

    percentage_errors = [
        abs(row["error"]) / abs(row["actualGeneration"]) * 100
        for row in valid
        if row["actualGeneration"] != 0
    ]

    mape = (
        sum(percentage_errors) / len(percentage_errors)
        if percentage_errors else None
    )

    return {
        "recordsEvaluated": len(valid),
        "missingActuals": missing_actuals,
        "missingForecasts": missing_forecasts,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "biasActualMinusForecast": round(bias, 2),
        "mapePercent": round(mape, 2) if mape is not None else None,
    }
