# Use an official Python runtime as a parent image
FROM python:3.9-slim

EXPOSE 5201
EXPOSE 5202
EXPOSE 5203
EXPOSE 5204
EXPOSE 5205
EXPOSE 5206

# Set the working directory in the container
WORKDIR /usr/src/app

# Install iperf3
RUN apt-get update && \
    apt-get install -y iperf3 && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the startup script
COPY start.sh .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME iperf3_exporter

# Run start.sh when the container launches
CMD ["./start.sh"]
