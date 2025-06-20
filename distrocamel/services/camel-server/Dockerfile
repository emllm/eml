FROM groovy:3.0-jdk11

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/camel-server/requirements.txt .
RUN pip3 install -r requirements.txt

# Copy Groovy scripts and config
COPY services/camel-server/src/ /app/src/
COPY config/ /app/config/

# Download Apache Camel Kamelets if needed
# RUN mkdir -p /app/kamelets && \
#     curl -L https://repo1.maven.org/maven2/org/apache/camel/kamelets/camel-kamelets-utils/0.9.0/camel-kamelets-0.9.0-utils.tar.gz | \
#     tar xz -C /app/kamelets

# Set the entrypoint
ENTRYPOINT ["groovy", "-cp", "/app/src:/app/config", "src/main/groovy/EmailProcessor.groovy"]
