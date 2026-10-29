import { useState } from "react";
import "./App.css";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [deliveryDate, setDeliveryDate] = useState("2026-01-15");
  const [cutoff, setCutoff] = useState("2026-01-14T12:00");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadAccuracy(event) {
    event?.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const params = new URLSearchParams({
        delivery_date: deliveryDate,
        cutoff: `${cutoff}:00Z`,
      });

      const response = await fetch(
        `${API_URL}/api/accuracy?${params.toString()}`,
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load accuracy data");
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Unable to connect to the backend. Check that your FastAPI server is running."
          : err.message || "Something went wrong. Please try again.",
      );

      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  const metrics = result?.metrics;

  return (
    <main className="dashboard">
      <header className="page-header">
        <p className="eyebrow">ENERGY ANALYTICS</p>
        <h1>Wind Forecast Accuracy</h1>
        <p>
          Compare day-ahead wind generation forecasts with actual generation.
        </p>
      </header>

      <form className="filters" onSubmit={loadAccuracy}>
        <label>
          Delivery date
          <input
            type="date"
            value={deliveryDate}
            onChange={(event) => setDeliveryDate(event.target.value)}
            required
          />
        </label>

        <label>
          Decision Cutoff (UTC)
          <input
            type="datetime-local"
            value={cutoff}
            onChange={(e) => setCutoff(e.target.value)}
          />
          <small>Enter the decision time in UTC, not your local time.</small>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Analyze forecast"}
        </button>
      </form>

      {metrics && (
        <>
          <section className="metric-grid">
            <MetricCard title="Mean Absolute Error" value={metrics.mae} />
            <MetricCard title="Root Mean Squared Error" value={metrics.rmse} />
            <MetricCard
              title="Forecast Bias"
              value={metrics.biasActualMinusForecast}
            />
            <MetricCard
              title="Mean Absolute Percentage Error"
              value={`${metrics.mapePercent}%`}
            />
          </section>

          <section className="panel">
            <h2>Hourly forecast comparison</h2>

            <div className="panel">
              <h2>Forecast vs Actual Generation</h2>
              <p className="muted">
                Hourly wind generation on {result.deliveryDate} (UTC)
              </p>

              <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={result.comparison.map((row) => ({
                      ...row,
                      hour: row.startTime.slice(11, 16),
                    }))}
                    margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                      dataKey="hour"
                      interval={2}
                      tick={{ fontSize: 12 }}
                    />

                    <YAxis
                      width={75}
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => value.toLocaleString()}
                    />

                    <Tooltip
                      formatter={(value, name) => [
                        value == null ? "Unavailable" : value.toLocaleString(),
                        name,
                      ]}
                      labelFormatter={(label) => `${label} UTC`}
                    />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="forecastGeneration"
                      name="Forecast"
                      stroke="#5265c7"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="actualGeneration"
                      name="Actual"
                      stroke="#15966a"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <p className="muted">
              {result.deliveryDate} · Cutoff: {result.decisionCutoff}
            </p>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Target time (UTC)</th>
                    <th>Forecast</th>
                    <th>Actual</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {result.comparison.map((row) => (
                    <tr key={row.startTime}>
                      <td>
                        {new Date(row.startTime).toISOString().slice(11, 16)}
                      </td>
                      <td>{row.forecastGeneration.toLocaleString()}</td>
                      <td>
                        {row.actualGeneration == null
                          ? "—"
                          : row.actualGeneration.toLocaleString()}
                      </td>
                      <td>
                        {row.error == null ? "—" : row.error.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="muted">
              {metrics.recordsEvaluated} matched hourly records evaluated ·{" "}
              {metrics.missingActuals} missing actuals ·{" "}
              {metrics.missingForecasts} missing forecasts
            </p>
          </section>
        </>
      )}

      {loading && (
        <div className="status-message loading-message" role="status">
          <span className="spinner" aria-hidden="true"></span>
          Fetching wind generation data and calculating accuracy...
        </div>
      )}

      {error && (
        <div className="status-message error-message" role="alert">
          <strong>Unable to load data</strong>
          <p>{error}</p>

          <button
            type="button"
            onClick={() => loadAccuracy()}
            disabled={loading}
          >
            Try again
          </button>
        </div>
      )}
    </main>
  );
}

function MetricCard({ title, value }) {
  return (
    <article className="metric-card">
      <p>{title}</p>
      <strong>{value ?? "—"}</strong>
    </article>
  );
}

export default App;
