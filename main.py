from src.avalanche_forecast_processing import AvalancheForecastProcessing
from src.shape_gen import create_shape_legend
import os
import io


def touch(path):
    """Emulates the 'touch' command by creating the file at *path* if it does not exist.
    If the file exists, its modification time will be updated."""
    with io.open(path, "ab"):
        os.utime(path, None)


def main():
    afp = AvalancheForecastProcessing()
    afp.fetch_region_data()

    afp.fetch_forecast_data()

    results = afp._create_forecast_layer_region_shape(afp.get_region("3003"))

    create_shape_legend(results)

    touch("./data/reload.trigger")


if __name__ == "__main__":
    main()
