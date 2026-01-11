from src.avalanche_forecast_processing import AvalancheForecastProcessing
from src.shape_gen import create_shape_legend


def main():
    afp = AvalancheForecastProcessing()
    afp.fetch_region_data()

    afp.fetch_forecast_data()

    results = afp._create_forecast_layer_region_shape(afp.get_region("3003"))

    create_shape_legend(results)


if __name__ == "__main__":
    main()
