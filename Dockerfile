# Stage 1: Build the frontend assets
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files and install dependencies
# Note: package-lock.json is intentionally not committed (see .gitignore and PR #22).
# npm install works from package.json alone (generates a transient lock inside the layer).
COPY frontend/package.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Build the Python backend with dependencies
FROM python:3.9-slim-bullseye AS backend-builder
WORKDIR /app

# Install Gunicorn (prod WSGI server, not in base deps)
RUN pip install --no-cache-dir gunicorn

# Copy pyproject.toml and install production dependencies
COPY pyproject.toml ./
COPY meal_planner_app/ ./meal_planner_app/
RUN pip install --no-cache-dir .

# Stage 3: Final production image
FROM python:3.9-slim-bullseye AS final
WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy python packages and gunicorn binary from backend-builder
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=backend-builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy built React assets from the frontend-builder stage
COPY --from=frontend-builder /app/meal_planner_app/static/react_app/ /app/meal_planner_app/static/react_app/

# Copy only the app package (source layout for runtime paths + templates + static base)
# NO broad "COPY . ." which would pull in frontend/ node_modules, dev files, and cause root ownership
COPY meal_planner_app/ ./meal_planner_app/

# Explicitly copy start script (dev-only override, do NOT rely on broad copy)
COPY start_and_seed.sh ./start_and_seed.sh

# NOW fix ownership of everything (after ALL copies)
RUN chown -R appuser:appuser /app
RUN chmod +x /app/start_and_seed.sh || true

# Switch to the non-root user (AFTER copies + chown)
USER appuser

# Expose only the prod port
EXPOSE 5000

# Prod CMD: gunicorn serving the Flask app (no npm, no dev server, no debug)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "meal_planner_app.main:app"]
