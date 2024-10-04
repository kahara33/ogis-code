"""Converts JSON schemata and instances to a SQLite database.

Relies on SQL Expression Language of SQLAlchemy.
Uses no ORM (Object-Relational Mapping) or raw SQL.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from jsonschema import validate
from sqlalchemy import Column, Float, ForeignKey, MetaData, String, Table
from sqlalchemy import create_engine as _create_engine
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine

from rag_tabular.excel_to_csv import get_rag_tab_path
from util.catvar import DevPhase


def json_instance_to_pandas_series(
    json_obj: dict[str, Any], json_dir: Path, remove_phase_key: bool = True
) -> pd.Series:
    """Converts a JSON instance to a pandas Series."""
    # Validate `json_obj` against the schema
    phase_ja = json_obj["フェーズ"]
    json_schema_path = json_dir.joinpath(f"{phase_ja}/{phase_ja}.schema.json")
    with open(json_schema_path, "r", encoding="utf-8") as f:
        json_schema_obj: dict[str, Any] = json.load(f)
    validate(instance=json_obj, schema=json_schema_obj)
    # Remove keys that have null (None) values
    json_obj = {key: value for key, value in json_obj.items() if value is not None}
    if remove_phase_key:
        json_obj.pop("フェーズ")
    return pd.Series(json_obj)


def create_engine(db_path: Path) -> Engine:
    return _create_engine(f"sqlite:///{db_path}?charset=utf8", echo=False)


def define_db(excel_path: Path, db_path: Path | None = None) -> None:
    """Creates a database schema (metadata) from JSON schemata.

    Uses DDL (Data Definition Language) `CREATE TABLE` under the hood.
    """
    data_dir: Path = excel_path.parent
    if db_path is None:
        # If `excel_path` is `foo/bar.xlsx`, then `db_path` is `foo/bar.sqlite3`
        db_path = data_dir.joinpath(excel_path.stem + ".sqlite3")
    if db_path.exists():
        db_path.unlink()
        print(f"Deleted {db_path.resolve()}")

    engine = create_engine(db_path)
    metadata_obj = MetaData()
    Table(
        "systems",
        metadata_obj,
        Column("システム", String, primary_key=True, nullable=False),
        Column("説明", String, nullable=True),
    )
    for phase in DevPhase:
        json_phase_dir = data_dir.joinpath(f"json/{phase.ja}")
        json_schema_path = json_phase_dir.joinpath(f"{phase.ja}.schema.json")
        with open(json_schema_path, "r", encoding="utf-8") as f:
            json_schema_obj: dict[str, Any] = json.load(f)

            def columns():
                for key, value in json_schema_obj["properties"].items():
                    if key == "フェーズ":
                        continue
                    if key == "システム":
                        yield Column(
                            key,
                            String,
                            ForeignKey("systems.システム"),
                            primary_key=True,
                            nullable=False,
                        )
                    elif value["type"] == "string":
                        yield Column(key, String, primary_key=True, nullable=False)
                    elif value["type"] == ["number", "null"]:
                        yield Column(key, Float(precision=10), nullable=True)

            Table(
                f"{phase.name}",  # テーブル名は日本語にできない
                metadata_obj,
                *columns(),  # フィールド名は日本語のまま
            )
    metadata_obj.create_all(engine)
    print(f"Created {db_path.resolve()}")


def manipulate_db(excel_path: Path, db_path: Path | None = None) -> None:
    """Inserts JSON instances into the database.

    Uses DML (Data Manipulation Language) `INSERT INTO` under the hood.
    """
    data_dir: Path = excel_path.parent
    if db_path is None:
        # If `excel_path` is `foo/bar.xlsx`, then `db_path` is `foo/bar.sqlite3`
        db_path = data_dir.joinpath(excel_path.stem + ".sqlite3")
    engine = create_engine(db_path)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    with engine.begin() as conn:
        for phase in DevPhase:
            json_phase_dir = data_dir.joinpath(f"json/{phase.ja}")
            for json_path in json_phase_dir.iterdir():
                if json_path.suffixes != [".json"]:
                    continue
                with open(json_path, "r", encoding="utf-8") as f:
                    json_obj: dict[str, Any] = json.load(f)
                json_obj.pop("フェーズ")
                # upsert (insert or update) into the "systems" table
                stmt = insert(metadata_obj.tables["systems"]).values(
                    システム=json_obj["システム"]
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=["システム"])
                conn.execute(stmt)
                # insert into the phase-specific table
                stmt = insert(metadata_obj.tables[phase.name]).values(**json_obj)
                conn.execute(stmt)
    print(f"Updated {db_path.resolve()}")


def query_sql_db(
    json_obj: dict[str, Any],
    db_path: Path | None = None,
    remove_phase_key: bool = True,
) -> tuple[pd.Series, pd.DataFrame]:
    """Selects relevant data from the database.

    Uses DQL (Data Query Language) `SELECT FROM` under the hood.
    """
    phase = DevPhase.from_ja(json_obj["フェーズ"])
    excel_path: Path = get_rag_tab_path()
    data_dir: Path = excel_path.parent
    series = json_instance_to_pandas_series(
        json_obj, data_dir.joinpath("json"), remove_phase_key=remove_phase_key
    )
    if db_path is None:
        # If `excel_path` is `foo/bar.xlsx`, then `db_path` is `foo/bar.sqlite3`
        db_path = data_dir.joinpath(excel_path.stem + ".sqlite3")
    engine = create_engine(db_path)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    table = metadata_obj.tables[phase.name]  # TODO: get rid of MetaData here
    with engine.begin() as conn:
        stmt = select(
            *[
                table.c[key]
                for key, value in json_obj.items()
                if value is not None and key != "フェーズ"
            ]
        ).where(json_obj["算出方法"] == table.c["算出方法"])
        if "分類" in json_obj:
            stmt = stmt.where(json_obj["分類"] == table.c["分類"])
        result = conn.execute(stmt)
        df = pd.DataFrame(result, columns=result.keys())
    return series, df


def main():
    rag_tab_path: Path = get_rag_tab_path()
    define_db(rag_tab_path)
    manipulate_db(rag_tab_path)


if __name__ == "__main__":
    main()
