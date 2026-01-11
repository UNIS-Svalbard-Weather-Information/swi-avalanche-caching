from datetime import datetime
from loguru import logger
import os
import pandas as pd


colors = [
    "#9B2226",
    "#005F73",
    "#E9D8A6",
    "#BB3E03",
    "#94D2BD",
    "#EE9B00",
    "#CA6702",
    "#8D8D8D",
]


def create_shape_legend(results, path="./data/avalanche-forecast/"):
    os.makedirs(path, exist_ok=True)

    for day, ar in results.items():
        logger.info("Creating shapefile, mapnik configuration and legend")
        if ar["gdf"] is not None:
            ar["gdf"].to_crs(epsg=3857).to_file(f"{path}{day}.shp")

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

        legend_file_html = f"""
  <div
    style="
      font-size: 0.875rem;
      color: #6b7280;
      padding-top: 1rem;
      padding-bottom: 1rem;
    "
  >
    This layer was updated on
    <strong>{datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC</strong> based on the avalanche forecast
    published by <strong>Varsom.no</strong> and the <strong>Norwegian Meteorological Institute</strong> on the <strong>{pd.to_datetime(ar["forecast"].get("PublishTime", "NA")).strftime("%Y-%m-%d %H:%M")} UTC</strong>. It is valid for the <strong>{pd.to_datetime(ar["forecast"].get("ValidFrom", "NA")).strftime("%Y-%m-%d")}</strong>
  </div>

  <div>
  <img src="https://www.varsom.no/Content/Images/AvalancheDangerLevels/level-{ar["forecast"].get("DangerLevelName").split(" ")[0] if ar["forecast"].get("DangerLevelName") else "0"}.svg"><img>
  <p>Danger level {ar["forecast"].get("DangerLevelName") if ar["forecast"].get("DangerLevelName") else "Not Rated / NA"}</p>
  <p>{ar["forecast"].get("MainText", "NA")}</p>
  </div>
  """
        if ar["legend"] is not None:
            for c, (key, pb) in zip(colors, ar["legend"].items()):
                mapnik_file_xml += f"""    <Rule>
        <Filter><![CDATA[([problem_id] = {key})]]></Filter>
        <PolygonSymbolizer fill="{c}" fill-opacity="0.5" />
        <LineSymbolizer stroke="#8D8D8D" stroke-linejoin="round" stroke-width="1" />
        </Rule>
    """

                legend_file_html += f"""<div style="display: flex; align-items: flex-start; gap: 0.75rem">
            <div
            style="
                width: 1.25rem;
                height: 1.25rem;
                flex-shrink: 0;
                background-color: {c};
                opacity: 0.5;
                border: 1px solid #998100;
                border-radius: 2px;
            "
            ></div>
            <span style="font-size: 0.875rem">{pb.get("label", "Unknown")}</span>
            <p>{pb.get("description", "Unknown")}</p>
        </div>
        """

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

        legend_file_html += f"""<a
        href="{ar["url"]}"
        target="_blank"
        rel="noopener noreferrer"
        style="font-size: 0.75rem; color: #3b82f6; text-decoration: none"
      >
        View on Varsom &rarr;
      </a>
    </div>
  </div>
  """

        with open(f"{path}{day}.html", "w") as file:
            file.write(legend_file_html)
            logger.info(f"Writing {path}{day}.html")

        with open(f"{path}{day}.xml", "w") as file:
            file.write(mapnik_file_xml)
            logger.info(f"Writing {path}{day}.xml")
