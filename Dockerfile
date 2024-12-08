# Base image for shared dependencies
FROM python:3.12-slim AS base

# Set environment variables for better Python behavior
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry using the official installer
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

# Copy project dependency files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction

# Copy application code
COPY status_tiles ./status_tiles
COPY config.yml ./

##########
# Testing image with development dependencies
##########
FROM base AS testing

# Add tests and coverage configuration
COPY tests ./tests
COPY .coveragerc ./

# Install additional development dependencies
RUN poetry install --with dev --no-interaction

# Default COVERAGE value for local testing
ENV COVERAGE=85

# Entry point for running tests with dynamic coverage thresholds
ENTRYPOINT ["sh", "-c", "poetry run pytest --cov=status_tiles --cov-report=term-missing --cov-fail-under=${COVERAGE} tests"]

##########
# Production image, lean
##########
FROM base AS production

# Default entry point for production
CMD ["poetry", "run", "uvicorn", "status_tiles.main:app", "--host", "0.0.0.0", "--port", "8000"]
