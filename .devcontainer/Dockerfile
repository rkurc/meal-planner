# Stage 1: Base image with Python and Node.js
FROM python:3.9-bullseye AS base

# Install Node.js v20
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
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

# Install frontend dependencies, playwright browsers, and build assets
WORKDIR /app/frontend
RUN npm install
RUN npx playwright install --with-deps
RUN npm run build

# Stage 3: Final image for testing
FROM base AS final

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the application source code and built frontend
COPY --from=builder /app/ /app/

# Set a default command
CMD ["sleep", "infinity"]
