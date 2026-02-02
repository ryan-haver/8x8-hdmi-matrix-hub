FROM python:3.12-slim

LABEL maintainer="Your Name"
LABEL description="Unfolded Circle Remote 3 integration for OREI BK-808 HDMI Matrix"

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY driver.json .

# Create directory for persistent config
RUN mkdir -p /data

# Environment variables (can be overridden at runtime)
ENV UC_CONFIG_HOME=/data
ENV UC_DISABLE_MDNS_PUBLISH=false
ENV UC_INTEGRATION_INTERFACE=0.0.0.0
ENV UC_INTEGRATION_HTTP_PORT=9095
ENV REST_API_PORT=8080
ENV REST_API_ENABLED=true

# Expose both WebSocket and REST API ports
EXPOSE 9095 8080

# Health check - verify the port is listening (simple TCP check)
# We use netcat to check if the port is open, avoiding WebSocket handshake issues
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); result=s.connect_ex(('localhost', 9095)); s.close(); exit(0 if result==0 else 1)"

# Run the driver
CMD ["python", "src/driver.py"]
