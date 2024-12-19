#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo "CS_PYTHON ${CS_PYTHON}"

"${CS_PYTHON}" ./test/client.py
