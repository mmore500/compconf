FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

# Install build tools and GCC 13
# https://unix.stackexchange.com/a/752016/605206 RE python3-launchpadlib
# Install build tools, GCC 13, and Python3
RUN apt-get update \
    && apt-get install -y --no-install-recommends  \
        build-essential \
        cmake \
        gcc \
        git \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-wheel \
        rsync \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify GCC version
RUN gcc --version

# Verify Python version
RUN python3 --version

# Stage local files
COPY . /app

# Install python dependencies
RUN python3 -m pip install uv --break-system-packages \
    && python3 -m uv pip install --system --break-system-packages \
        -r /app/requirements.txt \
    && python3 -m uv pip install --system --break-system-packages "/app"

# Test
RUN python3 -m compconf --help

# Clean up
RUN apt-get clean \
    && rm -rf /root/.cache /tmp/* /app
