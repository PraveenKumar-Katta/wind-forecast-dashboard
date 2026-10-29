# Wind Forecast Accuracy Dashboard

A full-stack application that compares day-ahead wind generation forecasts with actual wind generation data from **Elexon** and evaluates forecast accuracy using statistical metrics.

The dashboard helps users understand how closely forecasted wind generation matches actual generation at a selected delivery date and decision cutoff.

## Features

- Fetches national-level wind generation actuals and forecasts from the Elexon BMRS API.
- Allows users to select a delivery date and forecast decision cutoff in UTC.
- Selects the latest eligible forecast published on or before the decision cutoff.
- Compares forecasts and actuals at matching hourly timestamps.
- Calculates Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, and Mean Absolute Percentage Error (MAPE).
- Displays forecast-versus-actual generation in an interactive line chart.
- Provides a comparison table with forecast values, actual values, and forecast errors.
- Includes loading indicators, error messages, retry functionality, and automated backend tests.

## Technology Stack

**Frontend**
- React
- Vite
- Recharts
- JavaScript
- CSS

**Backend**
- Python
- FastAPI
- HTTPX
- Pytest
- Pytest-asyncio

**Data Source**
- Elexon BMRS API

## Architecture

```text
wind-forecast-dashboard/
├── backend/
│   ├── main.py
│   ├── elexon.py
│   ├── metrics.py
│   └── test_metrics.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

- `backend/main.py` exposes the FastAPI endpoints.
- `backend/elexon.py` retrieves and filters data from Elexon.
- `backend/metrics.py` matches forecast and actual records and calculates accuracy metrics.
- `backend/test_metrics.py` contains automated tests.
- `frontend/src/App.jsx` implements the dashboard, API requests, chart, metrics, and comparison table.
- `frontend/src/App.css` contains the dashboard styling.

## Data Sources

### Wind generation actuals

Dataset: `FUELHH`

Endpoint:

https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream

The application filters actual generation records using the `WIND` fuel type and the selected delivery date.

### Wind generation forecasts

Dataset: `WINDFOR`

Endpoint:

https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream

The application retrieves forecast records and selects the latest eligible forecast vintage for each target timestamp.

## Forecast Selection Logic

The decision cutoff represents the time by which a forecast must have been published to be eligible for the day-ahead decision.

For each target timestamp:

1. Retrieve forecasts within the configured publication-time lookback window.
2. Exclude forecasts published after the decision cutoff.
3. Group eligible forecasts by target timestamp (`startTime`).
4. Select the forecast with the latest eligible `publishTime`.
5. Match the selected forecast to the actual record with the same `startTime`.

This prevents forecasts published after the decision cutoff from being used in the evaluation.

## Timestamp Matching and Data Resolution

The current implementation compares records at matching timestamps. The observed Elexon actual dataset contains half-hourly records, while the forecast dataset used in this implementation provides hourly records.

To avoid artificially duplicating hourly forecasts, the application compares only timestamps shared by the selected forecasts and actuals.

Consequently, a full delivery day can produce 24 evaluated hourly records rather than 48 half-hourly records.

## Accuracy Metrics

The forecast error convention used by the application is:

`Error = Actual Generation − Forecast Generation`

### Mean Absolute Error (MAE)

The average absolute difference between actual and forecast generation.

`MAE = mean(|Actual − Forecast|)`

Lower MAE indicates smaller average forecast errors.

### Root Mean Squared Error (RMSE)

The square root of the mean squared forecast errors.

`RMSE = sqrt(mean((Actual − Forecast)²))`

RMSE penalizes larger errors more heavily than MAE.

### Forecast Bias

The average signed forecast error.

`Bias = mean(Actual − Forecast)`

- Negative bias: forecasts were higher than actual generation on average.
- Positive bias: forecasts were lower than actual generation on average.
- Bias near zero: average over- and under-forecasting approximately offset each other.

### Mean Absolute Percentage Error (MAPE)

The average absolute percentage error, excluding records where actual generation is zero.

`MAPE = mean(|Actual − Forecast| / |Actual| × 100)`

MAPE is reported as unavailable if no valid non-zero actual values exist.

## Prerequisites

Install the following before running the project:

- Python 3.10 or later
- Node.js and npm
- Git

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/PraveenKumar-Katta/wind-forecast-dashboard.git
cd wind-forecast-dashboard
```

### 2. Set up the backend

From the project root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install fastapi uvicorn httpx pytest pytest-asyncio
```

Start the backend:

```powershell
uvicorn main:app --reload
```

The API will normally be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/api/health

### 3. Set up the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, usually:

http://localhost:5173

Ensure that the frontend API URL in `frontend/src/App.jsx` points to the running backend:

```javascript
const API_URL = "http://127.0.0.1:8000";
```

The backend must allow requests from the frontend origin through its CORS configuration.

## Running Tests

From the `backend` directory, with the virtual environment activated:

```powershell
pytest -v
```

The tests cover forecast-to-actual matching, accuracy calculations, zero actual generation, missing records, no matched records, and invalid forecast cutoff timestamps.

## Example Evaluation

The following example was evaluated during development:

- Delivery date: `2026-01-15`
- Decision cutoff: `2026-01-14T12:00:00Z`
- Matched hourly records: `24`
- MAE: `1173.17`
- RMSE: `1304.88`
- Bias (actual − forecast): `-1173.17`
- MAPE: `12.58%`

These are example results for the specified date and cutoff, not general performance guarantees.

## Limitations and Assumptions

- The current comparison uses national-level wind generation data from Elexon.
- Forecast and actual records are matched by exact `startTime`; no half-hourly interpolation or duplication of hourly forecasts is performed.
- Forecast retrieval is limited by the configured publication-time lookback window.
- MAPE excludes records with zero actual generation.
- Results depend on the availability and completeness of the source API data.
- The application evaluates wind generation forecast accuracy. It does not calculate exact electricity procurement volumes, procurement costs, or total system demand because those are outside the current data scope.
- The example decision cutoff is an explicit assumption because the assignment does not specify a single required cutoff time.

## AI Tools Disclosure

AI assistance was used during development for implementation guidance and documentation.

## License

No license has been specified yet. Add an appropriate license if required by the project owner or assignment.
