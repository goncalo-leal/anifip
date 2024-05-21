FROM python:3.10-slim

# Update the package list
RUN apt-get update

# Set the working directory
WORKDIR /anifip

# Copy the requirements file into the container at /anifip
COPY requirements.txt .

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy contents into the container at /anifip
COPY . ./

# Run the receiver
CMD ["python", "receiver.py"]