"""
Rule-based energy optimizer — guaranteed-working fallback.
─────────────────────────────────────────────────────────────
Priority:  Renewables → Battery → Diesel fills the gap
Enforces:  battery SOC floor (20%), generator min run-time (2 h)
─────────────────────────────────────────────────────────────
"""

import numpy as np
from config import (
    BATTERY_CAPACITY_KWH, BATTERY_SOC_MIN, BATTERY_SOC_MAX,
    BATTERY_INITIAL_SOC,
    BATTERY_CHARGE_RATE_KW, BATTERY_DISCHARGE_RATE_KW,
    BATTERY_CHARGE_EFF, BATTERY_DISCHARGE_EFF,
    DIESEL_MAX_KW, DIESEL_MIN_KW, DIESEL_FUEL_RATE,
    DIESEL_MIN_RUNTIME_H,
)


def rule_based_dispatch(
    load: np.ndarray,
    solar: np.ndarray,
    wind: np.ndarray,
    initial_soc: float = BATTERY_INITIAL_SOC,
    dt_h: float = 1.0,
) -> dict:
    """
    Hourly energy dispatch using simple priority rules.

    Algorithm each timestep:
      1. Use all available solar (up to load)
      2. Use all available wind  (up to remaining load)
      3. If deficit remains → discharge battery (respect 20 % floor)
      4. If still deficit   → start diesel (respect min-run 2 h)
      5. If surplus renew.  → charge battery (respect 100 % cap)
      6. Excess gen output  → charge battery opportunistically

    Returns dict of arrays (length T):
        solar_used, wind_used, battery_kw (+=discharge, −=charge),
        diesel_kw, battery_soc, unmet_kw, curtailed_kw, fuel_liters
    """
    T = len(load)
    out = {k: np.zeros(T) for k in [
        "solar_used", "wind_used", "battery_kw", "diesel_kw",
        "battery_soc", "unmet_kw", "curtailed_kw", "fuel_liters",
    ]}

    soc = initial_soc
    gen_remaining_h = 0  # hours left on current generator min-run commitment

    for t in range(T):
        remaining = load[t]

        # ── 1. Solar ────────────────────────────────────────────
        s_use = min(solar[t], remaining)
        out["solar_used"][t] = s_use
        remaining -= s_use
        excess_solar = solar[t] - s_use

        # ── 2. Wind ─────────────────────────────────────────────
        w_use = min(wind[t], remaining)
        out["wind_used"][t] = w_use
        remaining -= w_use
        excess_wind = wind[t] - w_use

        # ── 3. Battery discharge ────────────────────────────────
        if remaining > 0:
            avail_energy = (soc - BATTERY_SOC_MIN) * BATTERY_CAPACITY_KWH
            max_disch = min(BATTERY_DISCHARGE_RATE_KW,
                           avail_energy * BATTERY_DISCHARGE_EFF / dt_h)
            max_disch = max(0.0, max_disch)
            bd = min(remaining, max_disch)
            out["battery_kw"][t] += bd
            soc -= (bd / BATTERY_DISCHARGE_EFF) * dt_h / BATTERY_CAPACITY_KWH
            remaining -= bd

        # ── 4. Diesel ──────────────────────────────────────────
        need_gen = remaining > 0  # load still unmet
        gen_committed = gen_remaining_h > 0  # min-run not expired

        if need_gen or gen_committed:
            if need_gen:
                d = min(max(remaining, DIESEL_MIN_KW), DIESEL_MAX_KW)
                gen_remaining_h = DIESEL_MIN_RUNTIME_H  # (re)start commitment
            else:
                d = DIESEL_MIN_KW  # running at idle to honour min-run
            out["diesel_kw"][t] = d
            out["fuel_liters"][t] = d * DIESEL_FUEL_RATE * dt_h
            gen_remaining_h = max(0.0, gen_remaining_h - dt_h)

            # Diesel excess (when gen forced to run above load) → charge batt
            diesel_excess = max(0.0, d - remaining)
            remaining = max(0.0, remaining - d)

            if diesel_excess > 0:
                room = (BATTERY_SOC_MAX - soc) * BATTERY_CAPACITY_KWH
                bc = min(diesel_excess,
                         BATTERY_CHARGE_RATE_KW,
                         room / (BATTERY_CHARGE_EFF * dt_h))
                bc = max(0.0, bc)
                out["battery_kw"][t] -= bc  # negative = charge
                soc += (bc * BATTERY_CHARGE_EFF) * dt_h / BATTERY_CAPACITY_KWH

        out["unmet_kw"][t] = max(0.0, remaining)

        # ── 5. Charge battery with excess renewables ────────────
        excess_renew = excess_solar + excess_wind
        if excess_renew > 0 and soc < BATTERY_SOC_MAX:
            room = (BATTERY_SOC_MAX - soc) * BATTERY_CAPACITY_KWH
            bc = min(excess_renew,
                     BATTERY_CHARGE_RATE_KW,
                     room / (BATTERY_CHARGE_EFF * dt_h))
            bc = max(0.0, bc)
            out["battery_kw"][t] -= bc
            soc += (bc * BATTERY_CHARGE_EFF) * dt_h / BATTERY_CAPACITY_KWH
            excess_renew -= bc

        out["curtailed_kw"][t] = max(0.0, excess_renew)

        soc = np.clip(soc, BATTERY_SOC_MIN, BATTERY_SOC_MAX)
        out["battery_soc"][t] = soc

    # ── Summary ─────────────────────────────────────────────────
    total_fuel   = out["fuel_liters"].sum()
    total_diesel = (out["diesel_kw"] * dt_h).sum()
    total_unmet  = out["unmet_kw"].sum()
    print(f"[rules] Fuel: {total_fuel:.1f} L  |  "
          f"Diesel energy: {total_diesel:.0f} kWh  |  "
          f"Unmet: {total_unmet:.1f} kWh")
    return out
