"""Bio/device alignment model with bounded claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from hardware_profile import extract_noise_parameters, load_calibration, simulate_noise_trajectory


def normalize(series: np.ndarray) -> np.ndarray:
    std = np.std(series)
    if std == 0:
        return np.zeros_like(series)
    return (series - np.mean(series)) / std


def build_biosignal(time_axis: np.ndarray, phase_shift: float, seed: int = 67) -> np.ndarray:
    rng = np.random.default_rng(seed)
    low_freq = np.sin(2 * np.pi * 0.67 * time_axis + phase_shift)
    alpha = 0.2 * np.sin(2 * np.pi * 8.0 * time_axis + rng.uniform(0, 2 * np.pi))
    theta = 0.15 * np.sin(2 * np.pi * 5.0 * time_axis + rng.uniform(0, 2 * np.pi))
    noise = 0.05 * rng.normal(size=len(time_axis))
    return normalize(low_freq + alpha + theta + noise)


def alignment_metrics(target: np.ndarray, biosignal: np.ndarray) -> dict[str, float]:
    target = normalize(target)
    biosignal = normalize(biosignal)
    correlation = float(np.corrcoef(target, biosignal)[0, 1])
    analytic_target = np.unwrap(np.angle(np.fft.rfft(target)))
    analytic_bio = np.unwrap(np.angle(np.fft.rfft(biosignal)))
    phase_distance = float(np.mean(np.abs(analytic_target - analytic_bio)))
    score = float(correlation - 0.1 * phase_distance)
    return {
        "correlation": correlation,
        "phase_distance": phase_distance,
        "alignment_score": score,
    }


def run_simulation(duration_seconds: float, sample_rate_hz: float) -> dict[str, object]:
    time_axis = np.arange(int(duration_seconds * sample_rate_hz)) / sample_rate_hz
    target = np.sin(2 * np.pi * 0.67 * time_axis)
    aligned = build_biosignal(time_axis, phase_shift=0.0)
    misaligned = build_biosignal(time_axis, phase_shift=np.pi / 2)
    aligned_metrics = alignment_metrics(target, aligned)
    misaligned_metrics = alignment_metrics(target, misaligned)
    return {
        "mode": "simulation",
        "evidence_status": "simulation_baseline",
        "aligned": aligned_metrics,
        "misaligned": misaligned_metrics,
        "delta_alignment_score": aligned_metrics["alignment_score"] - misaligned_metrics["alignment_score"],
    }


def run_hardware_derived(calibration_path: str | None, duration_seconds: float, sample_rate_hz: float) -> dict[str, object]:
    calibration = load_calibration(calibration_path)
    params = extract_noise_parameters(calibration)
    report = simulate_noise_trajectory(params, duration_seconds=duration_seconds, sample_rate_hz=sample_rate_hz)
    target = np.array(report["time_series"]["coherence_proxy"], dtype=float)
    time_axis = np.array(report["time_series"]["time_s"], dtype=float)
    aligned = build_biosignal(time_axis, phase_shift=0.0)
    misaligned = build_biosignal(time_axis, phase_shift=np.pi / 2)
    aligned_metrics = alignment_metrics(target, aligned)
    misaligned_metrics = alignment_metrics(target, misaligned)
    return {
        "mode": "hardware-derived",
        "evidence_status": "hardware_derived_model",
        "noise_summary": report["summary"],
        "aligned": aligned_metrics,
        "misaligned": misaligned_metrics,
        "delta_alignment_score": aligned_metrics["alignment_score"] - misaligned_metrics["alignment_score"],
    }


def main() -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Run bounded bio/device alignment experiments.")
    parser.add_argument("--mode", choices=["simulation", "hardware-derived"], default="simulation")
    parser.add_argument("--calibration")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--sample-rate", type=float, default=20.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.mode == "simulation":
        result = run_simulation(args.duration, args.sample_rate)
    else:
        result = run_hardware_derived(args.calibration, args.duration, args.sample_rate)

    result["schema_version"] = "rfl.bio_quantum_transduction.v2"
    result["next_step"] = "Replace synthetic biosignals with real captures aligned to a non-imposed device trace."

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"mode={result['mode']}")
        print(f"delta_alignment_score={result['delta_alignment_score']:.4f}")

    return result


if __name__ == "__main__":
    main()
