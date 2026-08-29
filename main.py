import os

import requests
from loguru import logger

from src.avalanche_forecast_processing import AvalancheForecastProcessing
from src.shape_gen import create_shape_legend


def touch(path):
    """Emulates the 'touch' command by creating the file at *path* if it does not exist.
    If the file exists, its modification time will be updated."""
    with open(path, "ab"):
        os.utime(path, None)


def monitoring(endpoint, status="complete", msg=None):
    if endpoint:
        r = f"{endpoint}?{f'state={status}'}{f'&msg={msg}' if msg else ''}"
        response = requests.get(r)
        logger.info(f"GET request to {r} returned status code: {response.status_code}")
    else:
        logger.warning("SWI_AVALANCHE_MONITORING_ENDPOINT environment variable not set")


def main():
    endpoint = os.getenv("SWI_AVALANCHE_MONITORING_ENDPOINT")
    monitoring(endpoint, status="run")

    try:
        afp = AvalancheForecastProcessing()
        afp.fetch_region_data()

        afp.fetch_forecast_data()

        results = afp._create_forecast_layer_region_shape(afp.get_region("3003"))

        create_shape_legend(results)

        touch("./data/reload.trigger")

        monitoring(endpoint)

    except Exception as e:
        monitoring(endpoint, status="fail", msg=e)


if __name__ == "__main__":
    main()
