#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

./compile.sh
./execute.sh
