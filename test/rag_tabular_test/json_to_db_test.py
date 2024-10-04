"""Tests for the json_to_db module."""

import json

import pytest

from rag_tabular.excel_to_csv import get_rag_tab_path
from rag_tabular.json_to_db import query_sql_db
from util.catvar import DevPhase


@pytest.mark.parametrize("phase", DevPhase)
def test_json_and_db(phase: DevPhase):
    json_dir = get_rag_tab_path().parent.joinpath(f"json/{phase.ja}")
    for json_path in json_dir.iterdir():
        if json_path.suffixes != [".json"]:
            continue
        with open(json_path, "r", encoding="utf-8") as f:
            json_obj = json.load(f)
        _, whole_df = query_sql_db(json_obj)
        small_df = whole_df.loc[whole_df["システム"] == json_obj["システム"]]
        assert len(small_df) == 1
        assert small_df.iloc[0].to_dict() == {
            key: value
            for key, value in json_obj.items()
            if value is not None and key != "フェーズ"
        }


@pytest.mark.parametrize("phase", DevPhase)
def test_query(phase: DevPhase):
    json_dir = get_rag_tab_path().parent.joinpath(f"json/{phase.ja}")
    for json_path in json_dir.iterdir():
        if json_path.suffixes != [".json"]:
            continue
        with open(json_path, "r", encoding="utf-8") as f:
            json_obj = json.load(f)
        series, df = query_sql_db(json_obj)
        # assert that the series is "contained" in the dataframe
        assert (df == series).all(axis=1).sum() == 1
