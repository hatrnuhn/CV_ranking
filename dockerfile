# Use an official Python runtime as a parent image
FROM python:3.10-slim

ENV FLASK_ENV=production
ENV PORT=3001

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 3001

# Run the app using waitress in production, or flask run for development
CMD ["python", "main.py"]
