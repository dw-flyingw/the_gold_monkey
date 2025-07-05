# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y build-essential curl portaudio19-dev && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir uv

# Create a virtual environment
RUN python -m venv $VIRTUAL_ENV

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies with uv into the virtual environment
RUN uv sync --no-cache

# Copy the rest of the project
COPY . .

# Move server_start.log into logs directory if it exists
RUN if [ -f server_start.log ]; then mkdir -p logs && mv server_start.log logs/server_start.log; fi

# Expose Streamlit's default port
EXPOSE 8501

# Set environment variables for Streamlit (optional)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Default command to run the Streamlit app
CMD ["streamlit", "run", "main.py"] 