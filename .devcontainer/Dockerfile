# Use an official Python runtime as a parent image
# Using a -bullseye image for Debian 11 base, which is common and stable.
FROM python:3.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js, npm, and other necessary tools
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Copy the application files
COPY . /app/

# Install Python dependencies
RUN pip install .[dev]

# Install frontend dependencies and build assets
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Reset WORKDIR for any subsequent commands
WORKDIR /app

# Set a default command to keep the container running if used interactively
CMD ["sleep", "infinity"]
