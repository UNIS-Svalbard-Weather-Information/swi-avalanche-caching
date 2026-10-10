import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import shape_gen  # noqa: E402


def _forecast():
    return {
        "DangerLevelName": "3 Considerable",
        "MainText": "Wind slabs in lee slopes.",
        "PublishTime": "2026-10-10T06:30:00",
        "ValidFrom": "2026-10-11T00:00:00",
    }


def _result(legend):
    return {
        "gdf": None,
        "forecast": _forecast(),
        "legend": legend,
        "url": "https://www.varsom.no/snoskredvarsling/",
    }


def _run(tmp_path, results):
    shape_gen.create_shape_legend(
        results, path_shape=str(tmp_path / "data"), path_legend=str(tmp_path / "meta")
    )


def _load(tmp_path, day):
    path = tmp_path / "meta" / f"avalanche-forecast-{day}" / "legend.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_writes_json_for_each_day(tmp_path):
    legend = {
        7: {"label": "Wind slab", "description": "Fresh wind slabs."},
        3: {"label": "Persistent weak layer", "description": "Deep slabs."},
    }
    _run(tmp_path, {0: _result(legend), 1: _result(legend)})

    for day in (0, 1):
        data = _load(tmp_path, day)
        assert data["version"] == 1
        assert data["published"] == "2026-10-10T06:30:00Z"
        assert data["validFrom"] == "2026-10-11T00:00:00Z"
        assert data["updated"].endswith("Z")
        assert [i["id"] for i in data["items"]] == ["7", "3"]
        assert [i["fill"] for i in data["items"]] == shape_gen.COLORS[:2]
        assert data["items"][0]["label"] == "Wind slab"
        assert data["summary"]["level"] == 3
        assert data["summary"]["levelName"] == "3 Considerable"
        assert data["summary"]["iconUrl"].endswith("level-3.svg")
        assert data["links"] == [
            {
                "label": "View on Varsom",
                "url": "https://www.varsom.no/snoskredvarsling/",
            }
        ]


def test_no_problems_gives_empty_items(tmp_path):
    result = _result(None)
    result["forecast"]["DangerLevelName"] = "Not Rated"
    _run(tmp_path, {0: result})

    data = _load(tmp_path, 0)
    assert data["items"] == []
    assert data["summary"]["level"] is None
    assert data["summary"]["text"] == "Wind slabs in lee slopes."


def test_html_still_written_and_no_temp_files(tmp_path):
    _run(tmp_path, {0: _result(None)})

    files = sorted(
        p.name for p in (tmp_path / "meta" / "avalanche-forecast-0").iterdir()
    )
    assert files == ["legend.html", "legend.json"]


def test_missing_timestamps_become_null():
    ar = _result(None)
    ar["forecast"].pop("PublishTime")
    ar["forecast"]["ValidFrom"] = "NA"
    data = shape_gen.build_legend_json(ar, pd.Timestamp.now("UTC").to_pydatetime())
    assert data["published"] is None
    assert data["validFrom"] is None
