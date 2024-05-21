FROM --platform=linux/arm64 python:3.9-slim

# Install dependencies
RUN pip install ipfshttpclient

# Set the working directory
WORKDIR /app

# Copy your Python script into the container
COPY master.py /app/

# Set the command to run your Python script
CMD ["python", "master.py", "Vivaldi Winter (Allegro).mid"]
