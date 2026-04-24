#!/bin/bash
set -e

echo "Running complete FinSight Microservices Test Suite..."

# Assuming you have myenv conda environment as specified
# Uses conda run to automatically route pytest calls inside the env
conda run -n myenv pytest services/tests/ -v

echo "Testing phase complete!"
