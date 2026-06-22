# Build args for version consistency (used by docker-bake.hcl)
ARG PYTHON_VERSION=3.9
ARG NODE_VERSION=20

# Stage 1: Base image with Python and Node.js
FROM python:${PYTHON_VERSION}-bullseye AS base

# Install Node.js (hardcoded to 20 to ensure npm is present; bake can override via ARG if needed)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
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
RUN npm install
RUN npm run build

# Stage 3: Final image for testing
FROM base AS final

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the application source code and built frontend
COPY --from=builder /app/ /app/

# Make the startup script executable
RUN chmod +x /app/start_and_seed.sh

# Set a default command
CMD ["/app/start_and_seed.sh"]
