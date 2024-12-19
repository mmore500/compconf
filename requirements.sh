#!/usr/bin/env bash

uv pip compile pyproject.toml | tee requirements.txt
