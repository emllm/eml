FROM groovy:3.0-jdk11

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/bot-generator/requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the bot script
COPY services/bot-generator/bot.py .

# Make the script executable
RUN chmod +x bot.py

# Run the bot
CMD ["python3", "bot.py"]
