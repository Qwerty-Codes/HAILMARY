"""
Load forecasting model — XGBoost regressor.
═══════════════════════════════════════════════════════════════
THIS IS THE CORE ML COMPONENT.  Unlike solar/wind generation
(physics formulas), this model LEARNS the mapping from weather
conditions + time features + recent load history → future load.
═══════════════════════════════════════════════════════════════
"""

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from config import XGBOOST_PARAMS, FEATURE_COLS, TARGET_COL


# ── Training & Evaluation ────────────────────────────────────────

def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> XGBRegressor:
    """
    Train XGBoost regressor on historical load data.

    This is GENUINE ML — the model discovers patterns like:
      • Load ↑ when temperature ↓ (heating demand)
      • Load follows 24-h activity cycles
      • Seasonal shift between polar day and polar night
    """
    print("[model] Training XGBoost load forecaster ...")
    model = XGBRegressor(**XGBOOST_PARAMS)
    model.fit(X_train, y_train, verbose=False)

    # Print feature importances (good for judge Q&A)
    importances = dict(zip(FEATURE_COLS, model.feature_importances_))
    print("[model] Feature importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 50)
        print(f"    {feat:20s}  {imp:.4f}  {bar}")
    return model


def evaluate_model(
    model: XGBRegressor,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[dict, np.ndarray]:
    """
    Evaluate on hold-out test set.  Returns (metrics_dict, predictions).
    """
    y_pred = model.predict(X_test)

    metrics = {
        "mae_kw":   mean_absolute_error(y_test, y_pred),
        "rmse_kw":  np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2":       r2_score(y_test, y_pred),
        "mape_pct": float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100),
    }

    print("[model] ── Hold-out test metrics ──")
    print(f"    MAE :  {metrics['mae_kw']:.2f} kW")
    print(f"    RMSE:  {metrics['rmse_kw']:.2f} kW")
    print(f"    R²  :  {metrics['r2']:.4f}")
    print(f"    MAPE:  {metrics['mape_pct']:.2f}%")
    return metrics, y_pred


# ── Live / Rolling Forecast ──────────────────────────────────────

def rolling_forecast(
    model: XGBRegressor,
    forecast_weather: pd.DataFrame,
    last_known_load: float,
    recent_loads_24h: pd.Series,
) -> np.ndarray:
    """
    Predict load hour-by-hour for the forecast horizon, feeding each
    prediction back as the lag-1h feature for the next step.

    This is the LIVE INFERENCE path — during real operation you'd call
    this every hour with fresh weather-forecast data.

    Args:
        model:             Trained XGBRegressor.
        forecast_weather:  Weather forecast DataFrame (must have temperature,
                           wind_speed, irradiance columns and DatetimeIndex).
        last_known_load:   Most recent observed load (kW).
        recent_loads_24h:  Series of load values for the last 24+ hours
                           (used for lag_24h look-ups).

    Returns:
        Array of predicted load values, one per forecast timestep.
    """
    preds = []
    prev_load = last_known_load

    for i in range(len(forecast_weather)):
        row = forecast_weather.iloc[i]
        ts  = forecast_weather.index[i]

        # Build feature vector for this single timestep
        features = {
            "hour_of_day":  ts.hour,
            "day_of_year":  ts.dayofyear,
            "temperature":  row["temperature"],
            "wind_speed":   row["wind_speed"],
            "is_daylight":  int(row["irradiance"] > 10),
            "load_lag_1h":  prev_load,
        }

        # lag_24h: try actual history, then our own predictions
        ts_24h = ts - pd.Timedelta(hours=24)
        if ts_24h in recent_loads_24h.index:
            features["load_lag_24h"] = recent_loads_24h[ts_24h]
        elif len(preds) >= 24:
            features["load_lag_24h"] = preds[-24]
        else:
            features["load_lag_24h"] = last_known_load

        X = pd.DataFrame([features])[FEATURE_COLS]
        pred = float(model.predict(X)[0])
        preds.append(pred)
        prev_load = pred

    return np.array(preds)
