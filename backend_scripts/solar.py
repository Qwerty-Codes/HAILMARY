"""
Solar power generation — PHYSICS-BASED calculation (NOT ML).
══════════════════════════════════════════════════════════════
Formula:  power_kw = irradiance × area × efficiency × (1 − cloud_cover) / 1000
This is deterministic physics, not a learned model.
══════════════════════════════════════════════════════════════
"""

import numpy as np
import pandas as pd

from config import PANEL_AREA_M2, PANEL_EFFICIENCY


def calc_solar_power(irradiance: float, cloud_cover_frac: float) -> float:
    """
    Calculate instantaneous solar panel output (kW).

    PHYSICS-BASED — not ML.  In a real deployment you'd calibrate
    the efficiency factor against measured output.

    Args:
        irradiance:       W/m² (from weather data)
        cloud_cover_frac: 0.0–1.0

    Returns:
        Power output in kW (≥ 0).
    """
    power_kw = (
        irradiance * PANEL_AREA_M2 * PANEL_EFFICIENCY
        * (1.0 - cloud_cover_frac) / 1000.0
    )
    return max(0.0, power_kw)


def calc_solar_series(weather_df: pd.DataFrame) -> pd.Series:
    """
    Vectorised solar generation for an entire time series.

    Key polar behaviour:
      • Polar night (May–Jul at Maitri): irradiance ≈ 0 → zero output
      • Polar summer (Nov–Jan): 24-h sunlight → significant generation
      • Cloud cover reduces output proportionally
    """
    irr = weather_df["irradiance"].values
    cc  = weather_df["cloud_cover_frac"].values
    power = np.maximum(0.0, irr * PANEL_AREA_M2 * PANEL_EFFICIENCY * (1.0 - cc) / 1000.0)

    result = pd.Series(power, index=weather_df.index, name="solar_kw")

    # Seasonal report
    monthly = result.groupby(result.index.month).mean()
    peak_month = monthly.idxmax()
    zero_hours = (result < 0.01).sum()

    print(f"[solar] PHYSICS-BASED  mean={result.mean():.2f} kW, "
          f"peak month={peak_month} ({monthly.max():.2f} kW avg)")
    print(f"[solar]   Zero-output hours: {zero_hours}/{len(result)} "
          f"({100*zero_hours/len(result):.1f}%) — polar night effect")
    return result


if __name__ == "__main__":
    from weather import fetch_historical
    w = fetch_historical()
    s = calc_solar_series(w)
    print(s.describe())
