# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Copy package.json and install npm dependencies
COPY package.json ./
RUN npm install

# Copy the current directory contents into the container at /app
COPY . .

# Build CSS and React App
RUN npm run build

# Install any needed packages specified in pyproject.toml
RUN pip install --no-cache-dir .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=meal_planner_app/main.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
