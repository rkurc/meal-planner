# Build args for version consistency (used by docker-bake.hcl)
ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.9

# Stage 1: Build the frontend assets
# Use Node 20+ because Vite 7 + @tailwindcss/vite require Node >= 20.19
FROM node:${NODE_VERSION}-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files and install dependencies
# Use `npm ci` for reproducible builds (respects package-lock.json)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Build the Python backend with dependencies
FROM python:${PYTHON_VERSION}-slim-bullseye AS backend-builder
WORKDIR /app

# Install Gunicorn (prod WSGI server, not in base deps)
RUN pip install --no-cache-dir gunicorn

# Copy pyproject.toml and install production dependencies
COPY pyproject.toml ./
COPY meal_planner_app/ ./meal_planner_app/
RUN pip install --no-cache-dir .

# Stage 3: Final production image
FROM python:${PYTHON_VERSION}-slim-bullseye AS final
# Re-declare ARGs for clarity in this stage (matching how NODE_VERSION is handled).
# This ensures PYTHON_VERSION from docker-bake.hcl / CLI overrides fully controls
# the base image and any references (though COPY below uses version-agnostic paths).
ARG NODE_VERSION=20
ARG PYTHON_VERSION=3.9
WORKDIR /app

# Install Node.js using the (major part of) ARG. Nodesource setup scripts only support
# major versions (setup_20.x even for NODE_VERSION=20.19). This matches the logic in
# .devcontainer/Dockerfile and allows documented overrides like NODE_VERSION=20.19
# (required by Vite) to produce working images.
RUN NODE_MAJOR=$(echo "${NODE_VERSION}" | cut -d. -f1) && \
    apt-get update && apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages and gunicorn from the backend-builder stage.
# Use full-tree copies (/usr/local/lib and the gunicorn binary) so that the
# pythonX.Y/ subdirectory (e.g. python3.9 or python3.10) created by the
# matching PYTHON_VERSION builder stage is carried over without hardcoding
# the version string in this Dockerfile. This makes PYTHON_VERSION from
# docker-bake.hcl fully effective for site-packages and binaries.
COPY --from=backend-builder /usr/local/lib /usr/local/lib
COPY --from=backend-builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy built React assets from the frontend-builder stage
COPY --from=frontend-builder /app/meal_planner_app/static/react_app/ /app/meal_planner_app/static/react_app/

# Copy only the app package (source layout for runtime paths + templates + static base)
# NO broad "COPY . ." which would pull in frontend/ node_modules, dev files, and cause root ownership
COPY meal_planner_app/ ./meal_planner_app/

# Copy the rest of the application (brings frontend/ source + package files)
COPY . .
RUN chmod +x start_and_seed.sh

# Install frontend dependencies in the final image so "npm run dev" works.
# We do this as root before switching user. (Adds size but makes the unified
# start script succeed in the prod-style image.)
WORKDIR /app/frontend
RUN npm ci --no-audit --no-fund
WORKDIR /app

# Build legacy Tailwind CSS (for the old Jinja templates served at /recipes etc.)
# This prevents 404 on /static/css/dist/output.css when using legacy UI.
RUN npx --yes -p tailwindcss@3 -p postcss -p autoprefixer \
      tailwindcss \
      -i ./meal_planner_app/static/css/src/input.css \
      -o ./meal_planner_app/static/css/dist/output.css --minify || true

# Apply ownership to everything (including node_modules created above)
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose only the prod port
EXPOSE 5000

# Prod CMD: gunicorn serving the Flask app (no npm, no dev server, no debug).
# NOTE: -w 1 (single worker) is REQUIRED. The app uses process-local in-memory
# lists (recipes_db etc in crud.py). Multiple workers would have independent
# state, causing recipes to appear in list but 404 on detail fetches (load-balanced
# across workers) and other inconsistency bugs.
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "meal_planner_app.main:app"]
