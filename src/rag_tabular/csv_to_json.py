import io
import json
from pathlib import Path
from typing import Any

import pandas as pd

from rag_tabular.excel_to_csv import get_rag_tab_path
from util.catvar import DevPhase


def save_json_obj(json_obj: dict[str, Any], json_path: Path) -> None:
    if json_path.exists():
        json_path.unlink()
        print(f"Deleted {json_path.resolve()}")
    with io.open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(json_obj, json_file, ensure_ascii=False, indent=4)
        json_file.write("\n")  # Add newline at the end
    print(f"Created {json_path.resolve()}")


def csv_to_json_instance(data_dir: Path, json_dir: Path | None = None):
    csv_dir = data_dir.joinpath("csv")
    if not csv_dir.exists():
        raise FileNotFoundError("Call excel_to_csv.py first.")
    if json_dir is None:
        json_dir = data_dir.joinpath("json")
        json_dir.mkdir(exist_ok=True)
    for phase in DevPhase:
        csv_path = csv_dir.joinpath(f"{phase.ja}.csv")
        df = pd.read_csv(csv_path)
        json_phase_dir = json_dir.joinpath(phase.ja)
        json_phase_dir.mkdir(exist_ok=True)
        for idx, row in df.iterrows():
            # TODO: 現状00, 01, 02, ...となっているが, 桁数を自動的に決定するようにする
            json_path = json_phase_dir.joinpath(f"{phase.ja}_{idx:02}.json")
            json_str: str = row.to_json(force_ascii=False, orient="index")
            json_obj: dict[str, Any] = {"フェーズ": phase.ja}
            json_obj.update(json.loads(json_str))
            save_json_obj(json_obj, json_path)


def csv_to_json_schema(data_dir: Path, json_dir: Path | None = None):
    csv_dir = data_dir.joinpath("csv")
    if not csv_dir.exists():
        raise FileNotFoundError("Call excel_to_csv.py first.")
    if json_dir is None:
        json_dir = data_dir.joinpath("json")
        json_dir.mkdir(exist_ok=True)
    for phase in DevPhase:
        csv_path = csv_dir.joinpath(f"{phase.ja}.csv")
        df = pd.read_csv(csv_path)
        json_phase_dir = json_dir.joinpath(phase.ja)
        json_phase_dir.mkdir(exist_ok=True)
        json_schema_path = json_phase_dir.joinpath(f"{phase.ja}.schema.json")
        json_schema_obj: dict[str, Any] = {
            "フェーズ": {"type": "string", "enum": [phase.ja]},
        }
        required_columns: list[str] = ["フェーズ", "システム"]
        for column_name in df.columns:
            if column_name == "システム":
                json_schema_obj[column_name] = {
                    "type": "string",
                }

            elif column_name == "算出方法":
                json_schema_obj[column_name] = {
                    "type": "string",
                    "enum": ["合計値", "平均値", "中央値"],
                }
                required_columns.append(column_name)
            elif column_name == "分類":
                json_schema_obj[column_name] = {
                    "type": "string",
                    "enum": [
                        "全体",
                        "新規",
                        "修正",
                    ],
                }
                required_columns.append(column_name)
            else:
                json_schema_obj[column_name] = {
                    "type": ["number", "null"],
                }
        json_schema_obj = {
            "type": "object",
            "properties": json_schema_obj,
            "required": required_columns,
        }
        save_json_obj(json_schema_obj, json_schema_path)


def main():
    data_dir = get_rag_tab_path().parent
    csv_to_json_instance(data_dir)
    csv_to_json_schema(data_dir)


if __name__ == "__main__":
    main()
