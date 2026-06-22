FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /usr/local/bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps, no editable install)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY mankkoo/ ./mankkoo/

# Expose port (default Flask port)
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=mankkoo/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application via uv
CMD ["uv", "run", "flask", "run"]
