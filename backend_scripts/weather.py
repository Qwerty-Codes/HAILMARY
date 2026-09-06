"""
Weather data fetching from Open-Meteo API.
──────────────────────────────────────────
- Historical archive: real ERA5 reanalysis (free, no API key)
- Forecast: real NWP model output (free, no API key)
- Built-in CSV caching so repeated runs don't re-hit the API
"""

import os
import requests
import pandas as pd

from config import (
    STATION_LAT, STATION_LON, STATION_NAME,
    HIST_START, HIST_END, FORECAST_DAYS,
)

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
HOURLY_VARS = "temperature_2m,wind_speed_10m,cloud_cover,shortwave_radiation"


def _cache_path(prefix: str, lat: float, lon: float, extra: str = "") -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe = f"{prefix}_{lat}_{lon}_{extra}".replace(".", "p").replace("-", "m")
    return os.path.join(CACHE_DIR, f"{safe}.csv")


def _parse_response(data: dict) -> pd.DataFrame:
    """Convert Open-Meteo JSON response to a clean DataFrame."""
    hourly = data["hourly"]
    df = pd.DataFrame({
        "timestamp":  pd.to_datetime(hourly["time"]),
        "temperature": hourly["temperature_2m"],       # °C
        "wind_speed":  hourly["wind_speed_10m"],        # m/s
        "cloud_cover": hourly["cloud_cover"],           # 0-100 %
        "irradiance":  hourly["shortwave_radiation"],   # W/m²
    })
    df = df.set_index("timestamp").sort_index()
    df["cloud_cover_frac"] = df["cloud_cover"] / 100.0
    return df


def fetch_historical(
    lat: float = STATION_LAT,
    lon: float = STATION_LON,
    start_date: str = HIST_START,
    end_date: str = HIST_END,
) -> pd.DataFrame:
    """
    Fetch hourly historical weather from Open-Meteo archive API.
    Uses ERA5 reanalysis — global coverage including Antarctica.

    Returns DataFrame indexed by UTC timestamp with columns:
        temperature, wind_speed, cloud_cover, irradiance, cloud_cover_frac
    """
    cache = _cache_path("hist", lat, lon, f"{start_date}_{end_date}")
    if os.path.exists(cache):
        print(f"[weather] Loading cached historical data: {os.path.basename(cache)}")
        df = pd.read_csv(cache, parse_dates=["timestamp"], index_col="timestamp")
        if "cloud_cover_frac" not in df.columns:
            df["cloud_cover_frac"] = df["cloud_cover"] / 100.0
        return df

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start_date, "end_date": end_date,
        "hourly": HOURLY_VARS,
        "timezone": "UTC",
    }

    print(f"[weather] Fetching historical data for {STATION_NAME} "
          f"({lat}°, {lon}°)  {start_date} → {end_date} ...")

    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    df = _parse_response(resp.json())

    df.to_csv(cache)
    print(f"[weather]   ✓ {len(df)} hourly rows cached to {os.path.basename(cache)}")
    return df


def fetch_forecast(
    lat: float = STATION_LAT,
    lon: float = STATION_LON,
    days: int = FORECAST_DAYS,
) -> pd.DataFrame:
    """
    Fetch hourly weather forecast from Open-Meteo forecast API.
    Returns DataFrame with same columns as fetch_historical.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": HOURLY_VARS,
        "forecast_days": days,
        "timezone": "UTC",
    }

    print(f"[weather] Fetching {days}-day forecast for {STATION_NAME} ...")

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    df = _parse_response(resp.json())

    print(f"[weather]   ✓ {len(df)} hourly forecast rows")
    return df


if __name__ == "__main__":
    hist = fetch_historical()
    print("\n── Historical summary ──")
    print(hist.describe().round(2))
    print()
    fcast = fetch_forecast()
    print("\n── Forecast summary ──")
    print(fcast.describe().round(2))
