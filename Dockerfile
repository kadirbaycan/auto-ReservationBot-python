# ===========================
# VFS Automation - Production Dockerfile
# Multi-stage build for optimized image size
# ===========================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-enterprise.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-enterprise.txt

# Install Playwright browsers
RUN python -m playwright install --with-deps chromium

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 vfsuser && \
    mkdir -p /app/data /app/logs /app/documents /app/info && \
    chown -R vfsuser:vfsuser /app

# Copy application code
COPY --chown=vfsuser:vfsuser . .

# Switch to non-root user
USER vfsuser

# Expose ports
EXPOSE 5000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "mobile_app:app"]
