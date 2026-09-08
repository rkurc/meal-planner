# Build args for version consistency (used by docker-bake.hcl)
ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.9

# Official Node image — copy binaries instead of nodesource + apt gnupg.
# Debian bullseye-security has 404'd gnupg packages in CI
# (e.g. gnupg_2.2.27-2+deb11u3), which broke bake ci / e2e.
FROM node:${NODE_VERSION}-bullseye AS node-bin

# Stage 1: Base image with Python and Node.js
FROM python:${PYTHON_VERSION}-bullseye AS base

ENV DEBIAN_FRONTEND=noninteractive
# Isolate Node from Python's /usr/local so we do not clobber pip/python.
COPY --from=node-bin /usr/local /opt/node
ENV PATH="/opt/node/bin:${PATH}"
# Chromium runtime libs (not -dev, not libcups2). `playwright install
# --with-deps` and cups both pull avahi from debian-security, which 404s
# (libavahi-common-data_0.8-5+deb11u3). Headless Chromium does not need CUPS.
# bullseye-security InRelease can be expired in CI; skip Valid-Until/Date checks.
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update \
    && apt-get install -y --no-install-recommends \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libatspi2.0-0 \
        libdrm2 \
        libgbm1 \
        libasound2 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libxkbcommon0 \
        libxshmfence1 \
        libpango-1.0-0 \
        libcairo2 \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/* \
    && node --version && npm --version \
    && pip install --upgrade pip

# Stage 2: Builder with source code and dependencies
FROM base AS builder

WORKDIR /app

# Copy all application files
COPY . /app/

# Install Python dependencies
RUN pip install .[dev]

# Install frontend dependencies and build assets
WORKDIR /app/frontend
RUN npm ci
RUN npm run build

# Stage 3: Final image for testing
FROM base AS final
# Re-declare ARG PYTHON_VERSION for clarity in this final stage (like NODE_VERSION
# handling in the root Dockerfile). Ensures PYTHON_VERSION (from docker-bake.hcl)
# fully drives the version used in the inherited base and copied artifacts.
ARG PYTHON_VERSION=3.9

WORKDIR /app

# Copy installed Python packages and gunicorn from the builder stage.
# Use full-tree copies (/usr/local/lib and the specific gunicorn binary) so that
# the pythonX.Y/ subdirectory matching the PYTHON_VERSION used in the builder
# stage is brought in without any hardcoded 'python3.9' (or similar) path here.
# This makes PYTHON_VERSION from docker-bake.hcl the single source of truth.
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy the application source code and built frontend
COPY --from=builder /app/ /app/

# Make the startup script executable
RUN chmod +x /app/start_and_seed.sh

# Download Chromium here so CI does not run `playwright install --with-deps`
# (that path apt-gets Debian security packages and 404s, same class of flake
# as the old nodesource/gnupg install). python:bullseye already has the
# shared libraries Chromium needs to launch headless.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
WORKDIR /app/frontend
RUN npx playwright install chromium
WORKDIR /app

ENV MEAL_PLANNER_DB=/app/data/meal_planner.db
RUN mkdir -p /app/data

# Set a default command
CMD ["/app/start_and_seed.sh"]
