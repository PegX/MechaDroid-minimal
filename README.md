# MechaDroid

Android program representation preprocessing. This minimal release provides an executable, offline synthetic example of one part of the research system. It is **not a complete paper artifact or benchmark reproduction**.

## What runs

Synthetic method signatures → metadata parsing → instruction token normalization → a two-node call-graph report.

Included: Method-key parsing + Dalvik normalization + synthetic graph report. The command prints a structured JSON report; `--output` writes the same report to a file. Inputs are built into the demonstration, so no datasets, credentials, GPU, API requests or model downloads are needed at runtime.

## Quick start

Python 3.10+; run from this repository directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
mechadroid-demo
mechadroid-demo --output reports/demo.json
python -m pytest -q
```

Dependency installation requires access to a Python package index. A representative output is checked in at `examples/demo-output.json`. Floating-point results may vary slightly by PyTorch/platform version. The example is reproducible within the tested environment; dependencies are declared but not locked.

## Layout

- `src/android_llm_gnn/`: extracted components and the new `demo.py` entry point.
- `tests/`: component checks and repeatability checks.
- `examples/demo-output.json`: synthetic output from the installed command.
- `PROVENANCE.md` and `SOURCE-MANIFEST.json`: source mapping and modifications.
- `pyproject.toml`: dependencies, package discovery and CLI installation.

## Scope and extension

The edge is explicitly constructed from the synthetic example, not extracted from an APK. This release does not generate LLM embeddings, train a GNN or classify malware. A real pipeline would need independently licensed APK data, a call-graph extractor, encoder and validated detector.

No private corpora, weights, checkpoints, experiment outputs, original Git history, third-party repository copies, credentials, attack-generation runners or APK modification/deployment pipelines are included. These examples analyze synthetic model or program components only. They do not establish the security of real systems.

## License and attribution

No open-source license has been selected. Confirm ownership, collaborators' publication rights and third-party obligations before making a public release; then add the appropriate LICENSE and required notices. This preparation does not claim license clearance. See `PROVENANCE.md` for details.
