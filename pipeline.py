import os
import pandas as pd
from weather import fetch_historical
from load_synthetic import generate_synthetic_load
from features import build_features, split_train_test
from forecaster import train_model, evaluate_model, rolling_forecast
from solar import calc_solar_series
from wind import calc_wind_series
from optimizer_rules import rule_based_dispatch
from optimizer_lp import lp_dispatch

def run_pipeline() -> dict:
    """
    Execute the full pipeline on historical data only (no live forecast).
    """
    results = {}
    sep = "═" * 60

    print(f"\n{sep}")
    print("  STAGE 1 — Fetch historical weather")
    print(sep)
    hist_weather = fetch_historical()
    results["hist_weather"] = hist_weather

    print(f"\n{sep}")
    print("  STAGE 2 — Generate synthetic load")
    print(sep)
    load = generate_synthetic_load(hist_weather)
    results["load"] = load

    print(f"\n{sep}")
    print("  STAGE 3 — Feature engineering")
    print(sep)
    feat_df = build_features(hist_weather, load)
    X_train, y_train, X_test, y_test = split_train_test(feat_df)
    results["feat_df"] = feat_df
    results["X_test"] = X_test
    results["y_test"] = y_test

    print(f"\n{sep}")
    print("  STAGE 4 — Train XGBoost load forecaster  ★ ML ★")
    print(sep)
    model = train_model(X_train, y_train)
    results["model"] = model

    print(f"\n{sep}")
    print("  STAGE 5 — Evaluate on hold-out test set")
    print(sep)
    metrics, y_pred = evaluate_model(model, X_test, y_test)
    results["metrics"] = metrics
    results["y_pred"] = y_pred

    print(f"\n{sep}")
    print("  STAGE 6 — Physics-based solar & wind generation")
    print(sep)
    hist_solar = calc_solar_series(hist_weather)
    hist_wind  = calc_wind_series(hist_weather)
    results["hist_solar"] = hist_solar
    results["hist_wind"]  = hist_wind

    test_idx = y_test.index
    test_load  = y_test.values
    test_solar = hist_solar.reindex(test_idx).fillna(0).values
    test_wind  = hist_wind.reindex(test_idx).fillna(0).values

    return _run_optimizers(results, test_idx, test_load, test_solar, test_wind, hist_weather.reindex(test_idx), "test-period")

def _run_optimizers(results, time_idx, load_arr, solar_arr, wind_arr, weather_df, label):
    sep = "═" * 60

    print(f"\n{sep}")
    print(f"  STAGE 9 — Rule-based optimizer ({label})")
    print(sep)
    rules = rule_based_dispatch(load_arr, solar_arr, wind_arr)
    results["rules"] = rules

    print(f"\n{sep}")
    print(f"  STAGE 10 — LP optimizer ({label})")
    print(sep)
    lp = lp_dispatch(load_arr, solar_arr, wind_arr)
    results["lp"] = lp

    print(f"\n{sep}")
    print("  RESULTS — Fuel Savings Comparison")
    print(sep)

    fuel_rules = rules["fuel_liters"].sum()
    fuel_lp    = lp["fuel_liters"].sum()
    saved      = fuel_rules - fuel_lp
    pct        = (saved / fuel_rules * 100) if fuel_rules > 0 else 0
    cost_saved = saved * 250.0 # FUEL_COST_PER_LITER

    print(f"  Rule-based fuel:  {fuel_rules:>8.1f} L")
    print(f"  LP-optimal fuel:  {fuel_lp:>8.1f} L")
    print(f"  ────────────────────────────")
    print(f"  Fuel saved:       {saved:>8.1f} L  ({pct:.1f}%)")
    print(f"  Cost saved:      ₹{cost_saved:>8.0f}")
    print()

    results["fuel_rules_L"] = fuel_rules
    results["fuel_lp_L"]    = fuel_lp
    results["fuel_saved_L"] = saved
    results["fuel_saved_pct"] = pct
    results["cost_saved_inr"] = cost_saved
    results["time_index"]   = time_idx

    dashboard_df = pd.DataFrame({
        "timestamp":   time_idx,
        "load_kw":     load_arr,
        "temperature": weather_df["temperature"].values,
        "wind_speed":  weather_df["wind_speed"].values,
        "irradiance":  weather_df["irradiance"].values,
        "solar_avail": solar_arr,
        "wind_avail":  wind_arr,
        "rb_solar":    rules["solar_used"],
        "rb_wind":     rules["wind_used"],
        "rb_battery":  rules["battery_kw"],
        "rb_diesel":   rules["diesel_kw"],
        "rb_soc":      rules["battery_soc"],
        "lp_solar":    lp["solar_used"],
        "lp_wind":     lp["wind_used"],
        "lp_battery":  lp["battery_kw"],
        "lp_diesel":   lp["diesel_kw"],
        "lp_soc":      lp["battery_soc"],
    })
    results["dashboard_df"] = dashboard_df

    return results
