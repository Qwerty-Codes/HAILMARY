"""
Wind power generation — PHYSICS-BASED calculation (NOT ML).
══════════════════════════════════════════════════════════════
Standard turbine power curve with cut-in / rated / cut-out speeds.
The cut-out SAFETY SHUTDOWN at >25 m/s is a key polar demo moment.
══════════════════════════════════════════════════════════════
"""

import numpy as np
import pandas as pd

from config import (
    TURBINE_RATED_KW,
    TURBINE_CUT_IN,
    TURBINE_RATED_SPEED,
    TURBINE_CUT_OUT,
    TURBINE_COUNT,
)


def calc_wind_power_single(wind_speed: float) -> float:
    """
    Single-turbine output using a standard power curve.

    Regions:
      1. v < cut-in (3 m/s)       → 0 kW
      2. cut-in ≤ v < rated (12)   → cubic ramp  P_rated × ((v−v_ci)/(v_r−v_ci))³
      3. rated ≤ v ≤ cut-out (25)  → P_rated (flat)
      4. v > cut-out               → 0 kW  ⚠️ SAFETY SHUTDOWN

    PHYSICS-BASED — not ML.
    """
    if wind_speed < TURBINE_CUT_IN or wind_speed > TURBINE_CUT_OUT:
        return 0.0
    if wind_speed >= TURBINE_RATED_SPEED:
        return TURBINE_RATED_KW
    frac = (wind_speed - TURBINE_CUT_IN) / (TURBINE_RATED_SPEED - TURBINE_CUT_IN)
    return TURBINE_RATED_KW * (frac ** 3)


def calc_wind_series(weather_df: pd.DataFrame) -> pd.Series:
    """
    Vectorised wind generation for an entire time series.
    Multiplies single-turbine output by TURBINE_COUNT.
    """
    ws = weather_df["wind_speed"].values

    # Vectorised power curve
    power = np.zeros_like(ws)
    ramp = (ws >= TURBINE_CUT_IN) & (ws < TURBINE_RATED_SPEED)
    rated = (ws >= TURBINE_RATED_SPEED) & (ws <= TURBINE_CUT_OUT)

    frac = (ws[ramp] - TURBINE_CUT_IN) / (TURBINE_RATED_SPEED - TURBINE_CUT_IN)
    power[ramp] = TURBINE_RATED_KW * (frac ** 3)
    power[rated] = TURBINE_RATED_KW

    total = power * TURBINE_COUNT
    result = pd.Series(total, index=weather_df.index, name="wind_kw")

    shutdown = (ws > TURBINE_CUT_OUT).sum()
    print(f"[wind]  PHYSICS-BASED  mean={result.mean():.2f} kW, "
          f"max={result.max():.2f} kW")
    print(f"[wind]    Safety shutdowns (>{TURBINE_CUT_OUT} m/s): "
          f"{shutdown}/{len(result)} hours")
    return result


if __name__ == "__main__":
    from weather import fetch_historical
    w = fetch_historical()
    wind = calc_wind_series(w)
    print(wind.describe())
