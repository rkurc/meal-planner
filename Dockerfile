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

# Stage 3: Final production image — Python + prebuilt SPA. No Node, no apt.
FROM python:${PYTHON_VERSION}-slim-bullseye AS final
# Re-declare ARG so PYTHON_VERSION from docker-bake.hcl / CLI overrides
# fully control the base image (COPY paths below are version-agnostic).
ARG PYTHON_VERSION=3.9
WORKDIR /app

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

# App source first, then built SPA so a host leftover under
# meal_planner_app/static/react_app/ cannot overwrite the Vite build.
COPY meal_planner_app/ ./meal_planner_app/
COPY --from=frontend-builder /app/meal_planner_app/static/react_app/ /app/meal_planner_app/static/react_app/

# Persistent SQLite file (mount a volume over /app/data in production)
ENV MEAL_PLANNER_DB=/app/data/meal_planner.db
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose only the prod port
EXPOSE 5000

# Prod CMD: gunicorn serving the Flask app (no npm, no dev server, no debug).
# NOTE: -w 1 keeps a single writer against the SQLite file. Multiple workers
# can share the file (WAL) later; not enabled in this change.
CMD ["gunicorn", "-w", "1", "-t", "120", "-b", "0.0.0.0:5000", "meal_planner_app.main:app"]
