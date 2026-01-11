from datetime import datetime
from loguru import logger
import os
import pandas as pd
from typing import Dict, Any, Optional

# Define colors as constants
COLORS = [
    "#9B2226",
    "#005F73",
    "#E9D8A6",
    "#BB3E03",
    "#94D2BD",
    "#EE9B00",
    "#CA6702",
    "#8D8D8D",
]


def create_shape_legend(
    results: Dict[str, Any], path: str = "./data/avalanche-forecast/"
) -> None:
    """
    Create shapefile, mapnik configuration and legend for avalanche forecasts.

    Args:
        results: Dictionary containing forecast data and geodataframes.
        path: Path to save the output files.

    Raises:
        ValueError: If required data is missing or invalid.
        IOError: If there's an issue writing files.
    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise

    for day, ar in results.items():
        try:
            logger.info(f"Processing data for day: {day}")

            # Check if required data exists
            if "gdf" not in ar or "forecast" not in ar:
                raise ValueError(f"Missing required data for day {day}")

            # Save shapefile if geodataframe exists
            if ar["gdf"] is not None:
                try:
                    ar["gdf"].to_crs(epsg=3857).to_file(f"{path}{day}.shp")
                    logger.info(f"Saved shapefile for {day}")
                except Exception as e:
                    logger.error(f"Failed to save shapefile for {day}: {e}")
                    continue

            # Generate mapnik XML file
            mapnik_file_xml = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE Map[]>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over">
  <Parameters>
    <Parameter name="bounds">0,50,50,90</Parameter>
    <Parameter name="format"><![CDATA[png8]]></Parameter>
    <Parameter name="name"><![CDATA[Avalanche Forecast]]></Parameter>
    <Parameter name="attribution"><![CDATA[Met Norway & Varsom]]></Parameter>
    <Parameter name="tilejson"><![CDATA[2.0.0]]></Parameter>
    <Parameter name="scheme"><![CDATA[xyz]]></Parameter>
  </Parameters>
  <Style name="avalanche_style_simple">
"""

            # Generate legend HTML with minimal CSS
            legend_file_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        .legend-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        .legend-color {{
            width: 24px;
            height: 24px;
            margin-right: 12px;
            flex-shrink: 0;
        }}
        .legend-label {{
            font-weight: bold;
            margin-right: 8px;
        }}
        .danger-level {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        .danger-icon {{
            width: 150px;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div>
        <div class="danger-level">
            <img src="https://www.varsom.no/Content/Images/AvalancheDangerLevels/level-{ar["forecast"].get("DangerLevelName", "0").split(" ")[0]}.svg" class="danger-icon">
            <div>
                <div class="legend-label">Danger level {ar["forecast"].get("DangerLevelName", "Not Rated / NA")}</div>
                <div>{ar["forecast"].get("MainText", "NA")}</div>
            </div>
        </div>
"""

            # Add legend items if legend data exists
            if ar["legend"] is not None:
                for i, (key, pb) in enumerate(
                    zip(ar["legend"].keys(), ar["legend"].values())
                ):
                    color = COLORS[i % len(COLORS)]
                    mapnik_file_xml += f"""    <Rule>
        <Filter><![CDATA[([problem_id] = {key})]]></Filter>
        <PolygonSymbolizer fill="{color}" fill-opacity="0.5" />
        <LineSymbolizer stroke="#8D8D8D" stroke-linejoin="round" stroke-width="1" />
        </Rule>
    """

                    legend_file_html += f"""
    <div class="legend-item">
        <div class="legend-color" style="background-color: {color}; opacity: 0.5; border: 1px solid #998100;"></div>
        <div>
            <div class="legend-label">{pb.get("label", "Unknown")}</div>
            <div>{pb.get("description", "Unknown")}</div>
        </div>
    </div>
    """

            # Close the mapnik XML file
            mapnik_file_xml += f"""  </Style>
  <Layer name="avalanche_layer" srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over">
    <StyleName>avalanche_style_simple</StyleName>
    <Datasource>
      <Parameter name="file">./{day}.shp</Parameter>
      <Parameter name="type">shape</Parameter>
    </Datasource>
  </Layer>
</Map>
  """

            # Close the legend HTML
            legend_file_html += f"""
    
    This layer was updated on
    <strong>{datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC</strong> based on the avalanche forecast
    published by <strong>Varsom.no</strong> and the <strong>Norwegian Meteorological Institute</strong> on the <strong>{pd.to_datetime(ar["forecast"].get("PublishTime", "NA")).strftime("%Y-%m-%d %H:%M")} UTC</strong>. It is valid for the <strong>{pd.to_datetime(ar["forecast"].get("ValidFrom", "NA")).strftime("%Y-%m-%d")}</strong>
    <br>
    
    <a href="{ar.get("url", "#")}" target="_blank" rel="noopener noreferrer">
        View on Varsom →
    </a>
</div>
</body>
</html>
  """

            # Write files with explicit UTF-8 encoding
            try:
                with open(f"{path}{day}.html", "w", encoding="utf-8") as file:
                    file.write(legend_file_html)
                    logger.info(f"Wrote legend HTML for {day}")
            except IOError as e:
                logger.error(f"Failed to write HTML file for {day}: {e}")

            try:
                with open(f"{path}{day}.xml", "w", encoding="utf-8") as file:
                    file.write(mapnik_file_xml)
                    logger.info(f"Wrote mapnik XML for {day}")
            except IOError as e:
                logger.error(f"Failed to write XML file for {day}: {e}")

        except Exception as e:
            logger.error(f"Error processing day {day}: {e}")
            continue
