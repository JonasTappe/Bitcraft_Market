# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1


# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (none strictly required for these python libs but good practice to keep in mind)
# RUN apt-get update && apt-get install -y gcc

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app code into the container
COPY . /app

# Create data directory just in case
RUN mkdir -p /app/data

# Expose the port the app runs on
EXPOSE 8052

# Make sure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# Command to run the app
ENTRYPOINT ["/app/entrypoint.sh"]
