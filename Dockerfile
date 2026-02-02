# 8x8 HDMI Matrix Hub - Multi-stage Dockerfile
#
# Supports HDCVT HDP-MXC88A-based matrix switches including:
# OREI BK-808, BZBGEAR BG-8K-88MA, A-NeuVideo ANI-8-8K60-S, and more.
#
# Build targets:
#   docker build .                    # Default: full build with UC support
#   docker build --target api-only .  # API-only (no UC dependencies)
#   docker build --target full .      # Explicit full build

# =============================================================================
# Stage 1: Base image with core API dependencies
# =============================================================================
FROM python:3.12-slim AS base

LABEL maintainer="ryan@zelu.io"
LABEL description="8x8 HDMI Matrix Hub - REST API and integrations"

WORKDIR /app

# Install core dependencies (no UC-specific packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY web/ ./web/
COPY run.py driver.json ./

# Create directory for persistent config
RUN mkdir -p /data

# Core environment variables
ENV UC_CONFIG_HOME=/data
ENV REST_API_PORT=8080
ENV WEBUI_ENABLED=true
ENV LOG_LEVEL=INFO

# =============================================================================
# Stage 2: API-only image (no UC dependencies)
# =============================================================================
FROM base AS api-only

# Disable UC integration
ENV UC_ENABLED=false

# Only expose REST API port
EXPOSE 8080

# Health check for API
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); result=s.connect_ex(('localhost', 8080)); s.close(); exit(0 if result==0 else 1)"

CMD ["python", "run.py"]

# =============================================================================
# Stage 3: Full image with UC integration support
# =============================================================================
FROM base AS full

# Install UC-specific dependencies
COPY requirements-uc.txt .
RUN pip install --no-cache-dir -r requirements-uc.txt

# Enable all integrations
ENV UC_ENABLED=true
ENV UC_DISABLE_MDNS_PUBLISH=false
ENV UC_INTEGRATION_INTERFACE=0.0.0.0
ENV UC_INTEGRATION_HTTP_PORT=9095

# Expose both WebSocket and REST API ports
EXPOSE 9095 8080

# Health check - verify UC integration port is listening
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); result=s.connect_ex(('localhost', 9095)); s.close(); exit(0 if result==0 else 1)"

CMD ["python", "run.py"]
