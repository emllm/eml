FROM groovy:3.0-jdk11

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/client-agent/requirements.txt .
RUN pip3 install -r requirements.txt

# Copy Groovy scripts
COPY services/client-agent/src/ /app/src/

# Create deployment directory
RUN mkdir -p /app/deployment

# Set the entrypoint
ENTRYPOINT ["groovy", "-cp", "/app/src", "src/main/groovy/ClientAgent.groovy"]
