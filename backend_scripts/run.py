#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  AI-Driven Smart Energy Management for Polar Research Stations  ║
║  SIH 2024 — Problem Statement 26061 (MoES / NCPOR)             ║
╚══════════════════════════════════════════════════════════════════╝

Entry point.  Run:
    python run.py                 # full pipeline with live forecast
    python run.py --offline       # skip live forecast (use test set)
    python run.py --no-plots      # skip matplotlib charts
"""

import sys
import os
import numpy as np
import pandas as pd

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline


def save_plots(results: dict, out_dir: str):
    """Generate and save all dashboard-ready charts."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    os.makedirs(out_dir, exist_ok=True)

    # ── 1. Predicted vs Actual Load (test set) ───────────────────
    if "y_test" in results and "y_pred" in results:
        y_test = results["y_test"]
        y_pred = results["y_pred"]
        metrics = results["metrics"]

        fig, ax = plt.subplots(figsize=(14, 5))
        # Plot a manageable window (last 7 days of test)
        n_show = min(168, len(y_test))
        idx = y_test.index[-n_show:]
        ax.plot(idx, y_test.values[-n_show:],
                label="Actual (synthetic)", linewidth=1.2, alpha=0.8)
        ax.plot(idx, y_pred[-n_show:],
                label="Predicted (XGBoost)", linewidth=1.2, alpha=0.8,
                linestyle="--")
        ax.set_title(f"Load Forecast — Predicted vs Actual  "
                     f"(MAE={metrics['mae_kw']:.1f} kW, R²={metrics['r2']:.3f})")
        ax.set_ylabel("Load (kW)")
        ax.set_xlabel("Time (UTC)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "01_load_forecast.png"), dpi=150)
        plt.close(fig)
        print(f"[plot] Saved 01_load_forecast.png")

    # ── 2. Source Mix — Stacked Area (LP optimizer) ──────────────
    if "dashboard_df" in results:
        df = results["dashboard_df"]

        for prefix, label in [("lp", "LP-Optimal"), ("rb", "Rule-Based")]:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                            gridspec_kw={"height_ratios": [3, 1]},
                                            sharex=True)

            ts = df["timestamp"]
            solar   = df[f"{prefix}_solar"].values
            wind    = df[f"{prefix}_wind"].values
            batt    = np.maximum(0, df[f"{prefix}_battery"].values)
            diesel  = df[f"{prefix}_diesel"].values

            ax1.stackplot(ts, solar, wind, batt, diesel,
                         labels=["Solar", "Wind", "Battery", "Diesel"],
                         colors=["#FFD700", "#4FC3F7", "#66BB6A", "#EF5350"],
                         alpha=0.85)
            ax1.plot(ts, df["load_kw"], color="black",
                    linewidth=1.5, label="Load", linestyle="--")
            ax1.set_title(f"Energy Source Mix — {label}")
            ax1.set_ylabel("Power (kW)")
            ax1.legend(loc="upper right")
            ax1.grid(True, alpha=0.3)

            # Battery SOC subplot
            ax2.plot(ts, df[f"{prefix}_soc"] * 100, color="#66BB6A",
                    linewidth=1.5)
            ax2.axhline(y=20, color="red", linestyle=":", linewidth=1,
                       label="SOC Floor (20%)")
            ax2.set_ylabel("Battery SOC (%)")
            ax2.set_xlabel("Time (UTC)")
            ax2.set_ylim(0, 105)
            ax2.legend(loc="upper right")
            ax2.grid(True, alpha=0.3)

            fig.autofmt_xdate()
            fig.tight_layout()
            fname = f"02_source_mix_{prefix}.png"
            fig.savefig(os.path.join(out_dir, fname), dpi=150)
            plt.close(fig)
            print(f"[plot] Saved {fname}")

    # ── 3. Fuel Comparison Bar Chart ─────────────────────────────
    if "fuel_rules_L" in results:
        fig, ax = plt.subplots(figsize=(8, 5))
        fuel_r = results["fuel_rules_L"]
        fuel_l = results["fuel_lp_L"]
        bars = ax.bar(["Rule-Based", "LP-Optimal"],
                      [fuel_r, fuel_l],
                      color=["#EF5350", "#4FC3F7"], width=0.5)
        ax.set_ylabel("Total Fuel (Litres)")
        ax.set_title(f"Fuel Consumption Comparison  "
                     f"(saved {results['fuel_saved_pct']:.1f}%)")

        # Annotate
        for bar, val in zip(bars, [fuel_r, fuel_l]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f"{val:.1f} L", ha="center", va="bottom", fontweight="bold")

        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "03_fuel_comparison.png"), dpi=150)
        plt.close(fig)
        print(f"[plot] Saved 03_fuel_comparison.png")

    # ── 4. Feature Importances ───────────────────────────────────
    if "model" in results:
        from config import FEATURE_COLS
        model = results["model"]
        imp = model.feature_importances_
        idx_sorted = np.argsort(imp)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh([FEATURE_COLS[i] for i in idx_sorted],
                imp[idx_sorted], color="#7E57C2")
        ax.set_xlabel("Importance")
        ax.set_title("XGBoost Feature Importances — Load Forecaster")
        ax.grid(True, axis="x", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "04_feature_importance.png"), dpi=150)
        plt.close(fig)
        print(f"[plot] Saved 04_feature_importance.png")

    print(f"\n[plot] All charts saved to {out_dir}/")


def main():
    no_plots = "--no-plots" in sys.argv

    print("=" * 64)
    print("  AI-Driven Smart Energy Management System")
    print("  Polar Research Station: Maitri, Antarctica")
    print("=" * 64)

    results = run_pipeline()

    # Save dashboard CSV
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)

    if "dashboard_df" in results:
        csv_path = os.path.join(out_dir, "dashboard_data.csv")
        results["dashboard_df"].to_csv(csv_path, index=False)
        print(f"\n[output] Dashboard data saved to {csv_path}")

    if not no_plots:
        try:
            save_plots(results, out_dir)
        except ImportError:
            print("\n[output] matplotlib not installed — skipping plots.")
            print("         Install with:  pip install matplotlib")
        except Exception as e:
            print(f"\n[output] Plot generation failed: {e}")
            print("         Run with --no-plots to skip.")

    # ── Final summary ────────────────────────────────────────────
    print("\n" + "=" * 64)
    print("  FINAL SUMMARY")
    print("=" * 64)
    if "metrics" in results:
        m = results["metrics"]
        print(f"  Load Forecaster (XGBoost):  MAE={m['mae_kw']:.2f} kW, "
              f"R²={m['r2']:.4f}, MAPE={m['mape_pct']:.2f}%")
    if "fuel_saved_L" in results:
        print(f"  Fuel saved (LP vs rules):  "
              f"{results['fuel_saved_L']:.1f} L  "
              f"({results['fuel_saved_pct']:.1f}%)  "
              f"= ₹{results['cost_saved_inr']:.2f}")
    print("=" * 64)
    print()

    return results


if __name__ == "__main__":
    main()
