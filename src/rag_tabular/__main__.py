"""Entry point for the package rag_tabular.

Converts the Excel file,
as specified by the environment variable `RAG_TAB_PATH`,
to a SQLite database file in the same directory.
Along the way, the Excel file is first converted to CSV files,
then the CSV files are converted to intermediate JSON files,
and finally the JSON files are converted to a SQLite database file.

For example, if the Excel file is `/foo/bar.xlsx`,
then the SQLite database file will be `/foo/bar.sqlite3`.
"""

from rag_tabular import csv_to_json, excel_to_csv, json_to_db

excel_to_csv.main()
csv_to_json.main()
json_to_db.main()
