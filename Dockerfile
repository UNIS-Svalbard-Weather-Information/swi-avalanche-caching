# Stage 1: Dependency resolution
FROM astral/uv:python3.13-bookworm-slim AS uv
WORKDIR /swi
COPY pyproject.toml uv.lock ./
# Export the locked, hashed set: the image installs exactly what uv.lock pins.
RUN uv export --frozen --no-dev --no-emit-project -o requirements.txt

# Stage 2: Build
FROM python:3.13-slim AS builder
WORKDIR /swi
COPY --from=uv /swi/requirements.txt .
# Install system dependencies required by rasterio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

# Stage 3: Runtime
FROM python:3.13-slim
WORKDIR /swi

# Install system dependencies required by rasterio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# The job never installs packages at runtime: remove pip (and its vendored copies of
# urllib3, msgpack, ...) so they are neither exposed nor flagged by image scanners.
RUN python -m pip uninstall -y pip setuptools wheel 2>/dev/null || true

# Copy application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x ./entrypoint.sh
RUN chmod +x ./run-cron.sh

# Use the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
