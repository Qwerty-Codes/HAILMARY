"""
Feature engineering for the load forecasting model.
Builds the feature matrix from weather + load history.
"""

import pandas as pd
import numpy as np

from config import FEATURE_COLS, TARGET_COL, TEST_SPLIT_FRACTION


def build_features(weather_df: pd.DataFrame, load_series: pd.Series) -> pd.DataFrame:
    """
    Build the feature matrix for load forecasting.

    Features (documented in config.FEATURE_COLS):
        hour_of_day   — 0–23, captures daily activity pattern
        day_of_year   — 1–366, captures polar-day / polar-night seasonality
        temperature   — °C, drives heating load
        wind_speed    — m/s, affects building heat loss & wind chill
        is_daylight   — binary, 1 if irradiance > 10 W/m² (polar regime flag)
        load_lag_1h   — autoregressive: load one hour ago
        load_lag_24h  — daily-cycle: load 24 hours ago

    Target:
        load_kw — hourly electrical load (kW)
    """
    df = weather_df.copy()
    df[TARGET_COL] = load_series

    # Time features
    df["hour_of_day"] = df.index.hour
    df["day_of_year"] = df.index.dayofyear

    # Polar daylight flag
    df["is_daylight"] = (df["irradiance"] > 10).astype(int)

    # Lag features — make the model autoregressive
    df["load_lag_1h"]  = df[TARGET_COL].shift(1)
    df["load_lag_24h"] = df[TARGET_COL].shift(24)

    # Drop rows where lags are NaN (first 24 hours)
    before = len(df)
    df = df.dropna(subset=["load_lag_1h", "load_lag_24h"])
    print(f"[features] Built feature matrix: {len(df)} rows "
          f"(dropped {before - len(df)} for lag warm-up)")
    return df


def split_train_test(
    df: pd.DataFrame,
    test_fraction: float = TEST_SPLIT_FRACTION,
):
    """
    Temporal train/test split — last `test_fraction` held out.
    NO random shuffling — this is time series data.
    """
    n = len(df)
    split_idx = int(n * (1 - test_fraction))

    train = df.iloc[:split_idx]
    test  = df.iloc[split_idx:]

    X_train, y_train = train[FEATURE_COLS], train[TARGET_COL]
    X_test,  y_test  = test[FEATURE_COLS],  test[TARGET_COL]

    print(f"[features] Train: {len(train):,} rows  "
          f"({train.index.min().date()} → {train.index.max().date()})")
    print(f"[features] Test:  {len(test):,} rows  "
          f"({test.index.min().date()} → {test.index.max().date()})")
    return X_train, y_train, X_test, y_test
