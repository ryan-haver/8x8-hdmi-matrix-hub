# 8x8 HDMI Matrix Hub - one image (docs/REMEDIATION_PLAN.md D11)
#
# Supports HDCVT HDP-MXC88A-based matrix switches including:
# OREI BK-808, BZBGEAR BG-8K-88MA, A-NeuVideo ANI-8-8K60-S, and more.
#
# One image with every integration's dependencies. The core (REST API, web UI,
# kiosk) always runs; integrations are switched on with environment variables:
#   UC_ENABLED=true   Unfolded Circle Remote 3 integration (WebSocket port 9095)
# A disabled integration is not imported and opens no port. See docs/DOCKER.md.
#
#   docker build -t hdmi-matrix-hub .
#
# The old build targets `full` and `api-only` are kept as aliases of the same
# image (UC is off unless UC_ENABLED=true); they will be removed in a later release.

FROM python:3.12-slim AS hub

LABEL org.opencontainers.image.title="8x8 HDMI Matrix Hub" \
      org.opencontainers.image.description="REST API, web UI, kiosk and integrations for 8x8 HDMI matrix switches" \
      org.opencontainers.image.source="https://github.com/ryan-haver/8x8-hdmi-matrix-hub" \
      org.opencontainers.image.licenses="MPL-2.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Core and integration dependencies (requirements-uc.txt includes requirements.txt).
COPY requirements.txt requirements-uc.txt ./
RUN pip install -r requirements-uc.txt

# Non-root user with a fixed UID/GID so a host data folder can be prepared for it
# (sudo chown -R 1000:1000 ./data). Override at build time with --build-arg.
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid "${APP_GID}" app \
 && useradd --uid "${APP_UID}" --gid app --no-create-home --home-dir /app --shell /usr/sbin/nologin appuser \
 && mkdir -p /data \
 && chown appuser:app /data

# Application code stays owned by root: the hub only writes to /data.
COPY src/ ./src/
COPY web/ ./web/
COPY run.py run_server.py driver.json ./
RUN python -m compileall -q src run.py

ENV DATA_DIR=/data \
    LOG_LEVEL=INFO \
    UC_ENABLED=false

# 8080: REST API, web UI (/ui), kiosk (/kiosk). 9095: Remote 3 integration (only when UC_ENABLED=true).
EXPOSE 8080 9095

# /api/health on the configured API_PORT (run.py resolves the same variables as the hub).
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD ["python", "run.py", "healthcheck"]

USER appuser

CMD ["python", "run.py"]

# Deprecated aliases of the one image (old `--target api-only` / `--target full` builds).
FROM hub AS api-only
FROM hub AS full

# Default target.
FROM hub
