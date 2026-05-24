#!/usr/bin/env bash
set -euo pipefail
python -m scripts.run_all_applications
python -m scripts.run_benchmark
python -m scripts.generate_diagrams
python -m scripts.generate_screenshots
python -m scripts.generate_report
python -m scripts.generate_ppt
python -m scripts.export_openapi
