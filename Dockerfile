# Use an official Python runtime as a parent image
FROM python:3.9

WORKDIR /app

# Install necessary build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Run the streamlit app when the container launches
CMD streamlit run --server.port $STREAMLIT_PORT --server.enableCORS true --browser.serverAddress 0.0.0.0 --browser.gatherUsageStats false /app/client.py