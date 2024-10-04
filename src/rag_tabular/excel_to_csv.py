import os
import unicodedata
from pathlib import Path

import pandas as pd

from util.catvar import DevPhase


def get_rag_tab_path() -> Path:
    """Returns the path to the Excel file representing the RAG tabular data.

    Raises: `ValueError` if the environment variable `RAG_TAB_PATH` is not properly set.
    """
    _rag_tab_path: str | None = os.getenv("RAG_TAB_PATH")
    if _rag_tab_path is None:
        raise ValueError("環境変数RAG_TAB_PATHを設定してください。")
    rag_tab_path = Path(_rag_tab_path)
    if not rag_tab_path.is_file():
        raise ValueError(
            f"ファイル {rag_tab_path} が見つかりません。"
            "環境変数RAG_TAB_PATHを正しく設定してください。"
        )
    if rag_tab_path.suffix != ".xlsx":
        raise ValueError(
            f"ファイル {rag_tab_path} はExcel (.xlsx) ファイルでなくてはなりません。"
            "環境変数RAG_TAB_PATHを正しく設定してください。"
        )
    return rag_tab_path


def excel_to_csv(
    excel_path: Path, phase: DevPhase, csv_path: Path | None = None
) -> None:
    df = read_excel(excel_path, phase)
    if csv_path is None:
        csv_dir = excel_path.parent.joinpath("csv")
        csv_dir.mkdir(exist_ok=True)
        csv_path = csv_dir.joinpath(f"{phase.ja}.csv")
    to_csv(df, csv_path)


def read_excel(data_path: Path, phase: DevPhase) -> pd.DataFrame:
    """Read Excel file and return DataFrame."""
    df = pd.read_excel(
        data_path,
        sheet_name=phase.ja,  # NOTE: シート名をあらかじめ指定
        header=[0, 1, 2],  # NOTE: ヘッダ行をあらかじめ指定
        skiprows=1,  # NOTE: 1行目をスキップ
        engine="openpyxl",  # openpyxlへの依存
    ).iloc[
        :, 1:
    ]  # NOTE: 1列目を削除
    flatten_header(df)
    return df


def standardize_column_name(column_name: str) -> str:
    """Standardize a column name."""
    if "Unnamed" in column_name:
        # blank column name is converted to "Unnamed*"
        return ""
    column_name = unicodedata.normalize("NFKC", column_name)  # NOTE: ユニコード正規化
    column_name = column_name.strip()  # NOTE: 前後の空白を削除
    column_name = column_name.replace("\n", "")  # NOTE: LFを削除
    column_name = column_name.replace("\r", "")  # NOTE: CRを削除
    column_name = column_name.replace("*", "")  # NOTE: *を削除
    # NOTE: "合計/平均" を "算出方法" に変換
    if column_name == "合計/平均":
        column_name = "算出方法"
    return column_name


def concatenate_column_names(column_names: tuple[str, ...]) -> str:
    """Standardize column names and join them with underscore ('_')."""
    column_names = tuple(
        standardize_column_name(column_name) for column_name in column_names
    )
    # NOTE: アンダースコア ('_') で結合
    concatenated_name: str = "_".join(
        column_name for column_name in column_names if column_name
    )
    if not concatenated_name:
        raise ValueError("All column names are 'Unnamed*'.")
    assert concatenated_name.count("_") <= len(column_names) - 1
    return concatenated_name


def flatten_header(df: pd.DataFrame) -> None:
    """Standardize and flatten multi-level headers in place."""
    df.columns = [
        concatenate_column_names(column_names) for column_names in df.columns.values
    ]
    if "算出方法" in df.columns:
        # NOTE: "算出方法"の値を"合計値", "平均値", "中央値"のいずれかに変換
        df["算出方法"] = df["算出方法"].replace("合計", "合計値")
        df["算出方法"] = df["算出方法"].replace("平均", "平均値")
        df["算出方法"] = df["算出方法"].replace("中央", "中央値")


def to_csv(df: pd.DataFrame, csv_path: Path) -> None:
    """Save DataFrame to CSV file."""
    # NOTE: 浮動小数点数を少数点以下10桁に設定
    if csv_path.exists():
        csv_path.unlink()
        print(f"Deleted {csv_path.resolve()}")
    df.to_csv(csv_path, index=False, float_format="%.10f")
    print(f"Created {csv_path.resolve()}")


def main() -> None:
    rag_tab_path: Path = get_rag_tab_path()
    for phase in DevPhase:
        excel_to_csv(rag_tab_path, phase)


if __name__ == "__main__":
    main()
