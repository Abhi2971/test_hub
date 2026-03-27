# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Base dependencies
# ============================================
FROM python:3.11-slim as base

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && useradd --create-home --shell /bin/bash app

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app/uploads /app/generated_pdfs && \
    chown -R app:app /app

# ============================================
# Stage 2: Builder
# ============================================
FROM base as builder

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Stage 3: Production
# ============================================
FROM base as production

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/generated_pdfs /app/logs && \
    chown -R app:app /app/uploads /app/generated_pdfs /app/logs

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Switch to non-root user
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command - Flask development
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]

# ============================================
# Stage 4: Celery worker variant
# ============================================
FROM production as celery-worker

USER root

# Install Redis CLI for health checks
RUN apt-get update && apt-get install -y --no-install-recommends redis-tools && \
    rm -rf /var/lib/apt/lists/*

USER app

CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info", "-Q", "default,email,results", "--concurrency=4"]

# ============================================
# Stage 5: Celery beat variant
# ============================================
FROM production as celery-beat

USER app

CMD ["celery", "-A", "app.celery", "beat", "--loglevel=info", "--scheduler", "celery.beat:PersistentScheduler"]

# ============================================
# Stage 6: Gunicorn production variant
# ============================================
FROM production as gunicorn

# Install gunicorn if not already in requirements
RUN pip install --no-cache-dir gunicorn

USER app

# Number of workers based on CPU cores
# Gunicorn recommended: 2-4 workers per core
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "run:app"]
