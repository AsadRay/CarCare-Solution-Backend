# Stage 1: Builder stage
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Health check (optional - remove if no health endpoint exists)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"

# Run the application with Gunicorn and eventlet for WebSocket support
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--worker-class", "eventlet", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "120", "run:app"]
