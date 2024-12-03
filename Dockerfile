# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy application files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the .env file is available in the container
ENV PYTHONUNBUFFERED=1
COPY .env /app/.env

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
