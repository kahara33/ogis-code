"""Tests for the csv_to_json module."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from jsonschema import validate

from rag_tabular.excel_to_csv import get_rag_tab_path
from util.catvar import DevPhase


@pytest.mark.parametrize("phase", DevPhase)
def test_csv_and_json_instance(phase: DevPhase):
    """Tests whether the CSV file is consistent with the JSON instances."""
    data_dir: Path = get_rag_tab_path().parent
    csv_path = data_dir.joinpath(f"csv/{phase.ja}.csv")
    df = pd.read_csv(csv_path)
    json_dir = data_dir.joinpath(f"json/{phase.ja}")
    for idx, csv_row in df.iterrows():
        json_path = json_dir.joinpath(f"{phase.ja}_{idx:02}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            json_obj: dict[str, Any] = json.load(f)
        # replace nan with None
        csv_row = csv_row.where(pd.notna(csv_row), None)
        csv_row_dict = csv_row.to_dict()
        csv_row_dict["フェーズ"] = phase.ja
        assert json_obj == csv_row_dict


@pytest.mark.parametrize("phase", DevPhase)
def test_csv_and_json_schema(phase: DevPhase):
    """Tests whether the CSV file is consistent with the JSON schema."""
    data_dir: Path = get_rag_tab_path().parent
    csv_path = data_dir.joinpath(f"csv/{phase.ja}.csv")
    df = pd.read_csv(csv_path)
    json_schema_path = data_dir.joinpath(f"json/{phase.ja}/{phase.ja}.schema.json")
    with open(json_schema_path, "r", encoding="utf-8") as f:
        json_schema_obj: dict[str, Any] = json.load(f)
    assert (
        list(json_schema_obj["properties"].keys()) == ["フェーズ"] + df.columns.tolist()
    )


@pytest.mark.parametrize("phase", DevPhase)
def test_json_instance_and_json_schema(phase: DevPhase):
    """Tests whether the JSON instances are consistent with the JSON schema."""
    data_dir: Path = get_rag_tab_path().parent
    json_dir = data_dir.joinpath(f"json/{phase.ja}")
    json_schema_path = json_dir.joinpath(f"{phase.ja}.schema.json")
    with open(json_schema_path, "r", encoding="utf-8") as f:
        json_schema_obj: dict[str, Any] = json.load(f)
    for json_path in json_dir.iterdir():
        if json_path.suffixes != [".json"]:
            continue
        with open(json_path, "r", encoding="utf-8") as f:
            json_obj: dict[str, Any] = json.load(f)
        validate(instance=json_obj, schema=json_schema_obj)
