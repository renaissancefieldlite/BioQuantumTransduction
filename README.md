# BioQuantumTransduction

Alignment model linking biosignal-like traces to a device-side coherence proxy.

This repo now distinguishes:

- `simulation_baseline`: synthetic biosignal alignment against a modeled carrier
- `hardware_derived_model`: the same alignment logic applied to a
  calibration-anchored coherence proxy
- `real_biosignal_validation`: pending

## What It Tests

Whether alignment metrics discriminate between an aligned and misaligned
biosignal under two conditions:

1. a known simulation carrier
2. a coherence proxy generated from device-style calibration parameters

## Quick Start

```bash
python3 bio_quantum_transduction.py --mode simulation --json
python3 bio_quantum_transduction.py --mode hardware-derived --json
```

See [docs/METHOD.md](docs/METHOD.md) and
[docs/EVIDENCE_BOUNDARY.md](docs/EVIDENCE_BOUNDARY.md).
