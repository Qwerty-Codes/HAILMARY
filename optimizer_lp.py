"""
Linear-Programming energy optimizer — polished version.
─────────────────────────────────────────────────────────────
Minimizes total diesel fuel over the planning horizon subject to:
  • Power balance every hour
  • Battery SOC bounds (20 %–100 %)
  • Charge / discharge rate limits
  • Generator capacity limits
Uses scipy.optimize.linprog (HiGHS solver, ships with scipy).
─────────────────────────────────────────────────────────────
NOTE:  Generator min-runtime is an integer constraint and is
omitted here to keep this a pure LP.  The rule-based optimizer
handles that constraint as a fallback.
─────────────────────────────────────────────────────────────
"""

import numpy as np
from scipy.optimize import linprog

from config import (
    BATTERY_CAPACITY_KWH, BATTERY_SOC_MIN, BATTERY_SOC_MAX,
    BATTERY_INITIAL_SOC,
    BATTERY_CHARGE_RATE_KW, BATTERY_DISCHARGE_RATE_KW,
    BATTERY_CHARGE_EFF, BATTERY_DISCHARGE_EFF,
    DIESEL_MAX_KW, DIESEL_FUEL_RATE,
)


def lp_dispatch(
    load: np.ndarray,
    solar_avail: np.ndarray,
    wind_avail: np.ndarray,
    initial_soc: float = BATTERY_INITIAL_SOC,
    dt_h: float = 1.0,
) -> dict:
    """
    Optimal energy dispatch via Linear Programming.

    Decision variables per timestep t (T timesteps, 5T total vars):
        s[t]  — solar used       ∈ [0, solar_avail[t]]
        w[t]  — wind used        ∈ [0, wind_avail[t]]
        d[t]  — diesel output    ∈ [0, DIESEL_MAX]
        bc[t] — battery charge   ∈ [0, CHARGE_RATE]
        bd[t] — battery discharge∈ [0, DISCHARGE_RATE]

    Objective:
        minimise  Σ d[t] × FUEL_RATE × dt

    Constraints:
        Power balance:  s[t] + w[t] + d[t] + bd[t] − bc[t] = load[t]
        SOC tracking:   soc(t) = soc₀ + Σ_{i≤t}(bc[i]·η_c − bd[i]/η_d)·dt / cap
        SOC bounds:     SOC_MIN ≤ soc(t) ≤ SOC_MAX

    Returns dict matching rule_based_dispatch output format.
    """
    T = len(load)
    N = 5 * T  # total variables

    # Variable index helpers
    def idx_s(t):  return t
    def idx_w(t):  return T + t
    def idx_d(t):  return 2 * T + t
    def idx_bc(t): return 3 * T + t
    def idx_bd(t): return 4 * T + t

    # ── Objective: minimise fuel ─────────────────────────────────
    c = np.zeros(N)
    for t in range(T):
        c[idx_d(t)] = DIESEL_FUEL_RATE * dt_h   # litres per step

    # ── Equality: power balance ──────────────────────────────────
    A_eq = np.zeros((T, N))
    b_eq = np.zeros(T)
    for t in range(T):
        A_eq[t, idx_s(t)]  =  1.0   # solar
        A_eq[t, idx_w(t)]  =  1.0   # wind
        A_eq[t, idx_d(t)]  =  1.0   # diesel
        A_eq[t, idx_bd(t)] =  1.0   # battery discharge
        A_eq[t, idx_bc(t)] = -1.0   # battery charge (consumes power)
        b_eq[t] = load[t]

    # ── Inequality: SOC bounds ───────────────────────────────────
    # soc(t) = soc₀ + Σ_{i=0}^{t} (bc[i]·η_c − bd[i]/η_d) · dt / cap
    #
    # Upper: soc(t) ≤ SOC_MAX
    #   → Σ (bc[i]·η_c − bd[i]/η_d) · dt / cap ≤ SOC_MAX − soc₀
    #
    # Lower: soc(t) ≥ SOC_MIN
    #   → −Σ (bc[i]·η_c − bd[i]/η_d) · dt / cap ≤ soc₀ − SOC_MIN

    n_ineq = 2 * T
    A_ub = np.zeros((n_ineq, N))
    b_ub = np.zeros(n_ineq)

    scale = dt_h / BATTERY_CAPACITY_KWH

    for t in range(T):
        # Upper SOC bound (row t)
        for i in range(t + 1):
            A_ub[t, idx_bc(i)] =  BATTERY_CHARGE_EFF * scale
            A_ub[t, idx_bd(i)] = -scale / BATTERY_DISCHARGE_EFF
        b_ub[t] = BATTERY_SOC_MAX - initial_soc

        # Lower SOC bound (row T + t)
        for i in range(t + 1):
            A_ub[T + t, idx_bc(i)] = -BATTERY_CHARGE_EFF * scale
            A_ub[T + t, idx_bd(i)] =  scale / BATTERY_DISCHARGE_EFF
        b_ub[T + t] = initial_soc - BATTERY_SOC_MIN

    # ── Variable bounds ──────────────────────────────────────────
    bounds = []
    for t in range(T):
        bounds.append((0, solar_avail[t]))          # s[t]
    for t in range(T):
        bounds.append((0, wind_avail[t]))            # w[t]
    for t in range(T):
        bounds.append((0, DIESEL_MAX_KW))            # d[t]
    for t in range(T):
        bounds.append((0, BATTERY_CHARGE_RATE_KW))   # bc[t]
    for t in range(T):
        bounds.append((0, BATTERY_DISCHARGE_RATE_KW))# bd[t]

    # ── Solve ────────────────────────────────────────────────────
    print(f"[lp] Solving LP: {N} variables, "
          f"{T} equality + {n_ineq} inequality constraints ...")

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")

    if not res.success:
        print(f"[lp] ⚠ Solver failed: {res.message}")
        print("[lp]   Falling back to rule-based dispatch.")
        from optimizer_rules import rule_based_dispatch
        return rule_based_dispatch(load, solar_avail, wind_avail,
                                   initial_soc, dt_h)

    x = res.x

    # ── Extract solution ─────────────────────────────────────────
    solar_used = np.array([x[idx_s(t)]  for t in range(T)])
    wind_used  = np.array([x[idx_w(t)]  for t in range(T)])
    diesel_kw  = np.array([x[idx_d(t)]  for t in range(T)])
    batt_ch    = np.array([x[idx_bc(t)] for t in range(T)])
    batt_dis   = np.array([x[idx_bd(t)] for t in range(T)])
    battery_kw = batt_dis - batt_ch   # positive = discharge, neg = charge
    fuel_liters = diesel_kw * DIESEL_FUEL_RATE * dt_h

    # Reconstruct SOC trajectory
    battery_soc = np.zeros(T)
    soc = initial_soc
    for t in range(T):
        soc += (batt_ch[t] * BATTERY_CHARGE_EFF
                - batt_dis[t] / BATTERY_DISCHARGE_EFF) * dt_h / BATTERY_CAPACITY_KWH
        soc = np.clip(soc, BATTERY_SOC_MIN, BATTERY_SOC_MAX)
        battery_soc[t] = soc

    total_fuel = fuel_liters.sum()
    total_diesel = (diesel_kw * dt_h).sum()
    print(f"[lp] ✓ Optimal fuel: {total_fuel:.1f} L  |  "
          f"Diesel energy: {total_diesel:.0f} kWh")

    return {
        "solar_used":  solar_used,
        "wind_used":   wind_used,
        "battery_kw":  battery_kw,
        "diesel_kw":   diesel_kw,
        "battery_soc": battery_soc,
        "unmet_kw":    np.zeros(T),  # LP guarantees load is met
        "curtailed_kw": solar_avail - solar_used + wind_avail - wind_used,
        "fuel_liters": fuel_liters,
    }
