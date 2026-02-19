# SWI Avalanche Caching System

A cron task to prepare map layers for displaying avalanche forecasts for the Svalbard Weather Information (SWI) system.

## Overview

This project fetches avalanche forecast data from the Norwegian Water Resources and Energy Directorate (NVE) API, processes it to create shapefiles and Mapnik configuration files for visualization.

## Features

- **Automated Data Fetching**: Retrieves avalanche forecast data from NVE API
- **Geospatial Processing**: Creates steepness contours and clips them with forecast regions
- **Map Layer Generation**: Generates shapefiles for map visualization
- **Legend Creation**: Produces HTML legends with danger levels and forecast details
- **Mapnik Integration**: Creates Mapnik XML configuration files for rendering
- **Docker Support**: Containerized deployment with uv for dependency management
- **Error Handling & Monitoring**: Comprehensive error handling with monitoring endpoint integration
- **Single Instance Execution**: Prevents multiple concurrent executions via process checking

## Installation

### Using Docker (Recommended)

```bash
# Build the Docker image
docker build -t swi-avalanche-caching .

# Run the container with volume mounts
docker run \
  -v ./data:/swi/data \
  -v ./static:/swi/static \
  swi-avalanche-caching
```

### Using uv

```bash
# Install dependencies with uv
uv pip install

# Run the script
uv run main.py
```

## Usage

The script generates:
- **Shapefiles**: `/swi/data/avalanche-forecast-{day}/{day}.shp` where day=0 (today), day=1 (tomorrow), etc.
- **Mapnik XML**: `/swi/data/avalanche-forecast-{day}/{day}.xml` - Mapnik configuration
- **Legend HTML**: `/swi/metadata/avalanche-forecast-{day}/legend.html` - Interactive legend
- **Reload trigger**: `/swi/data/reload.trigger` - File to trigger map reload

## Environment Variables

- `SWI_AVALANCHE_MONITORING_ENDPOINT`: URL endpoint for monitoring status updates (run/fail/complete)
- `DOCKER-CRON`: When set, keeps container running after execution for manual re-runs


## Volume Mounting

For optimal performance and to reduce compute costs, mount these volumes:
- `/swi/data` - For output files (shapefiles, reload trigger)
- `/swi/metadata` - For legend output
- `/swi/static` - For cached DEM files and steepness rasters (persistent storage)

## Key Components

- **AvalancheForecastProcessing**: Fetches and processes forecast data
- **MapsCaching**: Manages Digital Elevation Models and creates steepness contours
- **Shape Generation**: Creates shapefiles, Mapnik configs, and legends

## Data Sources

- NVE Avalanche Forecast API
- Norwegian Polar Institute Digital Elevation Models
- Varsom.no for danger level information

## Deployment

Set up a cron job for daily execution:

```bash
0 6 * * * /usr/bin/docker run \
  -e SWI_AVALANCHE_MONITORING_ENDPOINT="https://your-monitoring-endpoint.com" \
  -v /host/path/data:/swi/data \
  -v /host/path/metadata:/swi/metadata \
  -v /host/path/static:/swi/static \
  swi-avalanche-caching
```

For interactive debugging, use the `DOCKER-CRON` environment variable:

```bash
docker run \
  -e DOCKER-CRON=1 \
  -e SWI_AVALANCHE_MONITORING_ENDPOINT="https://your-monitoring-endpoint.com" \
  -v /host/path/data:/swi/data \
  -v /host/path/metadata:/swi/metadata \
  -v /host/path/static:/swi/static \
  -it swi-avalanche-caching
```

## License

See LICENSE.md for details.
