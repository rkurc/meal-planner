# Use an official Python runtime as a parent image
# Using a -bullseye image for Debian 11 base, which is common and stable.
FROM python:3.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js, npm, and other necessary tools
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copy the application files
COPY . /app/

# The postCreateCommand in devcontainer.json will handle dependency installation.
# This keeps the image build faster and dependencies can be updated without rebuilding the image.

# Set the default command to keep the container running
CMD ["sleep", "infinity"]
