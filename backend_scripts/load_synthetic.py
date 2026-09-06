"""
Synthetic load data generation.
────────────────────────────────────────────────────────────────
WHY SYNTHETIC:  Real Antarctic station load data is not publicly
available.  We generate realistic load profiles as a KNOWN
FUNCTION of real weather, then train our ML model to recover
that function.  This lets us:
  1. Validate the ML pipeline (we know ground truth)
  2. Demo the full system with realistic polar patterns
  3. Be transparent with judges about what's real vs. synthetic
────────────────────────────────────────────────────────────────
"""

import numpy as np
import pandas as pd

from config import (
    LOAD_BASE_KW,
    LOAD_HEATING_THRESHOLD_C,
    LOAD_HEATING_COEFF,
    LOAD_ACTIVITY_MULTIPLIER,
    LOAD_NOISE_STD,
)


def generate_synthetic_load(
    weather_df: pd.DataFrame,
    seed: int = 42,
) -> pd.Series:
    """
    Generate synthetic hourly load (kW) from real weather data.

    Formula:
        load = (base_load + heating_load) × activity_multiplier + noise

    Components:
        base_load  — constant always-on equipment (comms, servers)
        heating    — scales linearly with how far temp is below threshold
        activity   — time-of-day multiplier (crew awake vs. asleep)
        noise      — small Gaussian jitter for realism

    Args:
        weather_df: Must have 'temperature' column and DatetimeIndex.
        seed:       Random seed for reproducibility.

    Returns:
        pd.Series named 'load_kw', same index as weather_df.
    """
    rng = np.random.default_rng(seed)
    n = len(weather_df)

    # Base load — always on
    base = np.full(n, LOAD_BASE_KW)

    # Heating load — increases as temperature drops below threshold
    temp = weather_df["temperature"].values
    heating = np.maximum(0.0, LOAD_HEATING_THRESHOLD_C - temp) * LOAD_HEATING_COEFF

    # Activity multiplier — varies by hour of day
    hours = weather_df.index.hour
    activity = np.array([LOAD_ACTIVITY_MULTIPLIER[h] for h in hours])

    # Random noise
    noise = rng.normal(0, LOAD_NOISE_STD, n)

    # Combine
    load = (base + heating) * activity + noise

    # Clamp to realistic range
    load = np.clip(load, 20.0, 400.0)

    result = pd.Series(load, index=weather_df.index, name="load_kw")

    print(f"[load] Synthetic load generated: "
          f"mean={result.mean():.1f} kW, "
          f"min={result.min():.1f} kW, "
          f"max={result.max():.1f} kW")
    return result


if __name__ == "__main__":
    from weather import fetch_historical
    w = fetch_historical()
    load = generate_synthetic_load(w)
    print(load.describe())
