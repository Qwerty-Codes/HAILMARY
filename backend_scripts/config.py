"""
Polar Energy Management System — Configuration
All station parameters, equipment specs, and simulation settings in one place.
"""

# ── Station Coordinates ──────────────────────────────────────────
MAITRI_LAT  = -70.766
MAITRI_LON  =  11.732
BHARATI_LAT = -69.408
BHARATI_LON =  76.187

# Default station for the demo
STATION_LAT  = MAITRI_LAT
STATION_LON  = MAITRI_LON
STATION_NAME = "Maitri"

# ── Historical Data Range ────────────────────────────────────────
HIST_START     = "2023-01-01"
HIST_END       = "2024-06-30"       # ~18 months of data
FORECAST_DAYS  = 2                  # 48-hour forecast horizon

# ── Solar Panel Specs ────────────────────────────────────────────
# PHYSICS-BASED (not ML): power = irradiance × area × eff × (1 − cloud) / 1000
PANEL_AREA_M2    = 100.0            # 100 m² installed
PANEL_EFFICIENCY = 0.18             # 18% (typical polycrystalline)

# ── Wind Turbine Specs ───────────────────────────────────────────
# PHYSICS-BASED (not ML): standard power curve
TURBINE_RATED_KW    = 50.0          # Rated power per turbine
TURBINE_CUT_IN      = 3.0           # m/s — below this, no generation
TURBINE_RATED_SPEED = 12.0          # m/s — full power above this
TURBINE_CUT_OUT     = 25.0          # m/s — SAFETY SHUTDOWN ⚠️
TURBINE_COUNT       = 2             # Number of turbines

# ── Battery Storage ──────────────────────────────────────────────
BATTERY_CAPACITY_KWH     = 500.0
BATTERY_SOC_MIN          = 0.20     # 20% floor — NEVER breach this
BATTERY_SOC_MAX          = 1.00
BATTERY_INITIAL_SOC      = 0.60     # Start at 60%
BATTERY_CHARGE_RATE_KW   = 100.0    # Max charge rate
BATTERY_DISCHARGE_RATE_KW = 100.0   # Max discharge rate
BATTERY_CHARGE_EFF       = 0.92     # One-way charge efficiency
BATTERY_DISCHARGE_EFF    = 0.92     # One-way discharge efficiency

# ── Diesel Generator ────────────────────────────────────────────
DIESEL_MAX_KW       = 200.0         # Maximum output
DIESEL_MIN_KW       = 20.0          # Minimum stable output when running
DIESEL_FUEL_RATE    = 0.25          # Liters per kWh
DIESEL_MIN_RUNTIME_H = 2            # Minimum run time once started
FUEL_COST_PER_LITER = 250.0         # INR/liter (Antarctic logistics premium)

# ── Synthetic Load Generation ────────────────────────────────────
LOAD_BASE_KW             = 60.0     # Always-on base (comms, servers, lights)
LOAD_HEATING_THRESHOLD_C = -10.0    # Heating kicks in below this
LOAD_HEATING_COEFF       = 2.5      # kW per °C below threshold
LOAD_NOISE_STD           = 5.0      # Random noise std dev (kW)

# Activity multiplier by hour (UTC, roughly matches Maitri local time)
# Higher during "working hours," lower at night
LOAD_ACTIVITY_MULTIPLIER = [
    0.70, 0.65, 0.60, 0.60, 0.65, 0.70,   # 00-05: night
    0.80, 0.90, 1.00, 1.10, 1.15, 1.10,   # 06-11: morning ramp
    1.05, 1.10, 1.15, 1.10, 1.05, 1.00,   # 12-17: afternoon
    0.95, 0.90, 0.85, 0.80, 0.75, 0.70,   # 18-23: evening wind-down
]

# ── ML Model Settings ───────────────────────────────────────────
TEST_SPLIT_FRACTION = 0.20          # Last 20% of days for holdout
XGBOOST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}

FEATURE_COLS = [
    "hour_of_day",
    "day_of_year",
    "temperature",
    "wind_speed",
    "is_daylight",
    "load_lag_1h",
    "load_lag_24h",
]
TARGET_COL = "load_kw"
