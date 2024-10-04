import pytest
from streamlit.testing.v1 import AppTest

from util.api import API, APIType

# Relative to the present test module
APP_PATH = "../../app/pages/3_📝_分析.py"


def valid_openai_api():
    api = API.from_env(APIType.OPENAI)
    try:
        api.init_openai_client()
    except Exception:
        return False
    else:
        return True


@pytest.mark.skipif(not valid_openai_api(), reason="OpenAI API credentials not found")
def test():
    at = AppTest.from_file(APP_PATH).run()
    # Simulate the user uploading a JSON file
    at.session_state["json_obj"] = {
        "フェーズ": "要件定義",
        "システム": "システム１",
        "算出方法": "合計値",
        "分類": "全体",
        "プロダクト指標(外形)_ページ数_(頁)": 3355.0,
    }
    at.session_state["data_file_name"] = "data.json"
    at.session_state["data_file_size"] = 1234
    at.run()
    # Simulates the user entering OpenAI API credentials
    api = API.from_env(APIType.OPENAI)
    at.session_state["api"] = api
    at.run()
    # Simulate the user entering the analysis prompt
    at.text_area[0].set_value("時間がないので3行で分析してください。")
    # Simulates the user clicking the "分析を開始する" button
    at.button[0].click().run(timeout=60)
