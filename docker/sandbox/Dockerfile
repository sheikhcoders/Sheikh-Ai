FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    software-properties-common \
    xvfb \
    x11vnc \
    xterm \
    supervisor \
    python3 \
    python3-pip \
    git \
    unzip \
    novnc \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install websockify
RUN pip3 install websockify

# Set up working directory
WORKDIR /app

# Copy requirement files and install
COPY backend/sandbox_api/requirements.txt .
RUN pip3 install -r requirements.txt

# Install Playwright browsers and deps
RUN playwright install chromium
RUN playwright install-deps

# Copy the application code
COPY backend/sandbox_api /app/backend/sandbox_api

# Copy Supervisor configuration
COPY docker/sandbox/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
# API Server
EXPOSE 8000
# VNC (websockify)
EXPOSE 6080

# Default command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
