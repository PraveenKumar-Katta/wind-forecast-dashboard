import pytest
from metrics import compare_forecasts, calculate_metrics
from elexon import fetch_forecasts


def test_compare_forecasts():
    actuals = [
        {"startTime": "2026-01-15T00:00:00Z", "generation": 100},
        {"startTime": "2026-01-15T00:30:00Z", "generation": 120},
    ]

    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 110,
        }
    ]

    result = compare_forecasts(actuals, forecasts)

    assert len(result) == 1
    assert result[0]["actualGeneration"] == 100
    assert result[0]["forecastGeneration"] == 110
    assert result[0]["error"] == -10


def test_calculate_metrics():
    comparison = [
        {
            "actualGeneration": 100,
            "forecastGeneration": 110,
            "error": -10,
        },
        {
            "actualGeneration": 200,
            "forecastGeneration": 180,
            "error": 20,
        },
    ]

    metrics = calculate_metrics(comparison)

    assert metrics["recordsEvaluated"] == 2
    assert metrics["mae"] == 15
    assert metrics["rmse"] == 15.81
    assert metrics["biasActualMinusForecast"] == 5
    assert metrics["mapePercent"] == 10


def test_zero_actual_generation():
    """MAPE should exclude records where actual generation is zero."""
    comparison = [
        {
            "actualGeneration": 0,
            "forecastGeneration": 10,
            "error": -10,
        },
        {
            "actualGeneration": 100,
            "forecastGeneration": 90,
            "error": 10,
        },
    ]

    metrics = calculate_metrics(comparison)

    assert metrics["recordsEvaluated"] == 2
    assert metrics["mae"] == 10
    assert metrics["rmse"] == 10
    assert metrics["biasActualMinusForecast"] == 0
    assert metrics["mapePercent"] == 10


def test_all_actual_values_are_zero():
    """MAPE should be None when every actual value is zero."""
    comparison = [
        {
            "actualGeneration": 0,
            "forecastGeneration": 10,
            "error": -10,
        },
        {
            "actualGeneration": 0,
            "forecastGeneration": 20,
            "error": -20,
        },
    ]

    metrics = calculate_metrics(comparison)

    assert metrics["recordsEvaluated"] == 2
    assert metrics["mapePercent"] is None


def test_missing_actual_record():
    """A forecast without a matching actual should have no error."""
    actuals = [
        {"startTime": "2026-01-15T00:00:00Z", "generation": 100}
    ]

    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 110,
        },
        {
            "startTime": "2026-01-15T01:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 120,
        },
    ]

    comparison = compare_forecasts(actuals, forecasts)

    assert len(comparison) == 2
    assert comparison[0]["error"] == -10
    assert comparison[1]["actualGeneration"] is None
    assert comparison[1]["error"] is None


def test_missing_forecast_record():
    """An unmatched half-hourly actual should not create a forecast row."""
    actuals = [
        {"startTime": "2026-01-15T00:00:00Z", "generation": 100},
        {"startTime": "2026-01-15T00:30:00Z", "generation": 120},
    ]

    forecasts = [
        {
            "startTime": "2026-01-15T00:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 110,
        }
    ]

    comparison = compare_forecasts(actuals, forecasts)

    assert len(comparison) == 1
    assert comparison[0]["startTime"] == "2026-01-15T00:00:00Z"


def test_no_matching_records():
    """Metrics calculation should fail if no rows can be evaluated."""
    with pytest.raises(
        ValueError,
        match="No matched forecast and actual records",
    ):
        calculate_metrics([
            {
                "actualGeneration": None,
                "forecastGeneration": 100,
                "error": None,
            }
        ])

@pytest.mark.parametrize(
    "cutoff",
    [
        "not-a-date",
        "2026-01-14T12:00:00",  # No timezone
    ],
)
@pytest.mark.asyncio
async def test_invalid_cutoff(cutoff):
    with pytest.raises(ValueError):
        await fetch_forecasts("2026-01-15", cutoff)