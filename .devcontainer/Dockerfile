# Build args for version consistency (used by docker-bake.hcl)
ARG PYTHON_VERSION=3.9
ARG NODE_VERSION=20

# Stage 1: Base image with Python and Node.js
FROM python:${PYTHON_VERSION}-bullseye AS base

# Install Node.js using the (major part of) ARG so `docker buildx bake dev` / `ci` (and NODE_VERSION overrides)
# affect the nodesource setup. Nodesource setup scripts use major version only (e.g. 20.x even if NODE_VERSION=20.19).
# This replaces previous hardcode of setup_20.x .
ENV DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=20
RUN NODE_MAJOR=$(echo "${NODE_VERSION}" | cut -d. -f1) && \
    apt-get update && apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    # Upgrade pip
    pip install --upgrade pip

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

# Set a default command
CMD ["/app/start_and_seed.sh"]
