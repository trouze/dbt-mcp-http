FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install dbt Cloud CLI
RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update
RUN exec $SHELL

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/

# Copy SSH keys for git access (if needed)
RUN mkdir -p ./keys
COPY keys/ ./keys/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "dbt_mcp.http_server:app", "--host", "0.0.0.0", "--port", "8000"]