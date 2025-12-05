# Stage 1: Build the frontend assets
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Build the Python backend with dependencies
FROM python:3.9-slim-bullseye AS backend-builder
WORKDIR /app

# Install Gunicorn
RUN pip install gunicorn

# Copy pyproject.toml and install production dependencies
COPY pyproject.toml ./
COPY meal_planner_app/ ./meal_planner_app/
RUN pip install --no-cache-dir .

# Stage 3: Final production image
FROM python:3.9-slim-bullseye AS final
WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from the backend-builder stage
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=backend-builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy built frontend assets from the frontend-builder stage
COPY --from=frontend-builder /app/meal_planner_app/static/react_app/ /app/meal_planner_app/static/react_app/

# Copy the application source code
COPY meal_planner_app/ ./meal_planner_app/

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Copy the rest of the application
WORKDIR /app
COPY . .
RUN chmod +x start_and_seed.sh

# Expose ports
EXPOSE 5000 5173

# Default command (can be overridden)
CMD ["./start_and_seed.sh"]
