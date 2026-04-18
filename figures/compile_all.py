"""
figures/compile_all.py
Regenerate all CEDAR-PKD grant figures in a single command.

Runs the simulation pipeline first (writes irt_params.csv and
response_matrix.csv to outputs/), then generates all 8 figures in
numerical order.  Figures are saved to outputs/ as both 300 DPI PNG and PDF.

Usage
-----
    python figures/compile_all.py          # run from project root
    python figures/compile_all.py --fast   # skip IRT simulation (use cached)

Requirements
------------
    outputs/ will be created if it does not exist.
    All figure scripts import from simulation/ and models/ — run from root.
"""

import argparse
import os
import subprocess
import sys
import time

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Script manifest — ordered so simulation always runs before figures
# ---------------------------------------------------------------------------

SIMULATION_SCRIPT = os.path.join("simulation", "simulate.py")

FIGURE_SCRIPTS = [
    os.path.join("figures", "fig1_app_screenshot.py"),
    os.path.join("figures", "fig2_icc.py"),
    os.path.join("figures", "fig3_item_params.py"),
    os.path.join("figures", "fig4_taxonomy.py"),
    os.path.join("figures", "fig5_trajectories.py"),
    os.path.join("figures", "fig6_adaptive_vs_static.py"),
    os.path.join("figures", "fig7_demographic_paths.py"),
    os.path.join("figures", "fig8_cedar_birch.py"),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run(script_path, label):
    """Run one script via subprocess; return (success, elapsed_seconds)."""
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        cwd=_ROOT,
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n  ✗  {label} FAILED  ({elapsed:.1f}s)")
        print("  --- stdout ---")
        print(result.stdout)
        print("  --- stderr ---")
        print(result.stderr)
        return False, elapsed
    else:
        # Print any output from the script (e.g. "Saved: ...")
        for line in result.stdout.strip().splitlines():
            print(f"     {line}")
        print(f"  ✓  {label}  ({elapsed:.1f}s)")
        return True, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate all CEDAR-PKD grant figures."
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Skip IRT simulation (reuse cached outputs/irt_params.csv).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  CEDAR-PKD — compile_all.py")
    print("  Regenerating all 8 grant figures")
    print("=" * 60)

    total_t0  = time.time()
    failures  = []

    # ── Step 0: Simulation ─────────────────────────────────────────────────
    irt_csv = os.path.join(_ROOT, "outputs", "irt_params.csv")
    if args.fast and os.path.exists(irt_csv):
        print("\n[--fast] Skipping simulation — using cached irt_params.csv")
    else:
        print("\n[Step 0] Running IRT simulation...")
        ok, t = _run(SIMULATION_SCRIPT, "simulation/simulate.py")
        if not ok:
            failures.append(SIMULATION_SCRIPT)

    # ── Steps 1–8: Figure scripts ──────────────────────────────────────────
    print()
    for script in FIGURE_SCRIPTS:
        label = os.path.basename(script)
        fignum = label.replace("fig", "Fig ").split("_")[0].strip()
        print(f"[{fignum}] {label}")
        ok, t = _run(script, label)
        if not ok:
            failures.append(script)

    # ── Summary ────────────────────────────────────────────────────────────
    total_t = time.time() - total_t0
    print()
    print("=" * 60)
    if not failures:
        print(f"  All figures generated successfully  ({total_t:.1f}s total)")
        print(f"  Output directory: {os.path.join(_ROOT, 'outputs')}")
    else:
        print(f"  {len(failures)} script(s) failed:")
        for f in failures:
            print(f"    • {f}")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
