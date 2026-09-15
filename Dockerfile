FROM python:3.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Absolute path so StaticFiles() and save_thumbnail() are never
    # sensitive to the process CWD.  Override via .env if needed.
    UPLOAD_DIR=/app/uploads

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create runtime dirs and set permissions
RUN mkdir -p /app/logs /app/uploads/thumbnails /logs && \
    chmod 755 /logs

# Use non-root user (must own /app and /app/uploads so the volume mount is writable)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /logs
USER appuser

# Persist user-uploaded files across container rebuilds.
VOLUME ["/app/uploads"]

EXPOSE 8000

# Container-level health check (exercises /healthz)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
