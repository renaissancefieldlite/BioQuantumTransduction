# BioQuantumTransduction

This is the biosignal coupling layer for the 0.67 Hz stack.

It asks whether biological-style traces can lock onto a coherence-bearing signal strongly enough to matter, then checks that question under both synthetic and calibration-anchored conditions.

This repo now distinguishes:

- `simulation_baseline`: synthetic biosignal alignment against a modeled transition cadence
- `hardware_derived_model`: the same alignment logic applied to a
  calibration-anchored coherence proxy
- `real_biosignal_validation`: pending

## What It Tests

Whether alignment metrics discriminate between an aligned and misaligned
biosignal under two conditions:

1. a known simulation transition cadence
2. a coherence proxy generated from device-style calibration parameters

## Quick Start

```bash
python3 bio_quantum_transduction.py --mode simulation --json
python3 bio_quantum_transduction.py --mode hardware-derived --json
```

See [docs/METHOD.md](docs/METHOD.md) and
[docs/EVIDENCE_BOUNDARY.md](docs/EVIDENCE_BOUNDARY.md).
