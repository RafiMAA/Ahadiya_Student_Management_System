#!/bin/bash
unset PYTHONPATH
unset ROS_PACKAGE_PATH
unset AMENT_PREFIX_PATH
unset COLCON_PREFIX_PATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
