# ─────────────────────────────────────────────────────────
# OpenEnv Productivity — Dockerfile
# ─────────────────────────────────────────────────────────
FROM python:3.11-slim

# Metadata
LABEL maintainer="openenv-productivity"
LABEL description="OpenEnv Productivity AI Task Environment"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .



# Set Python path so imports resolve correctly
ENV PYTHONPATH="/app"

# Default environment overrides (can be overridden at runtime)
ENV OPENENV_MODEL="meta-llama/Llama-3.3-70B-Instruct"
ENV OPENENV_BASE_URL="https://api-inference.huggingface.co/v1"
ENV OPENENV_MAX_TOKENS="1024"
ENV OPENENV_TEMPERATURE="0.1"
ENV OPENENV_SLEEP="1.0"

# Health check: verify the environment can be imported
RUN python -c "from env.openenv import OpenEnv; env = OpenEnv(); obs = env.reset(); print('✓ Environment OK:', obs.task_type)"

# Default command: run the full inference benchmark
CMD ["python", "inference.py"]
