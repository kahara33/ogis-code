from streamlit.testing.v1 import AppTest

# Relative to the present test module
APP_PATH = "../../app/pages/1_📊_可視化.py"


def test_initial_state():
    at = AppTest.from_file(APP_PATH).run()
    assert at.session_state["json_obj"] is None
    assert len(at.title) == 1
    assert at.title[0].body == "データの可視化📊"
    assert len(at.error) == 1
    assert (
        at.error[0].body
        == "サイドバーを開き、システムデータをアップロードしてください。"
    )
    # TODO: Check the status for file_uploader


def test_upload():
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

    # Check the status for sidebar
    assert len(at.sidebar) == 1
    assert at.sidebar.success[0].body == "data.json (1.2KB) がアップロードされました。"
    assert len(at.sidebar.button) == 1
    assert at.sidebar.button[0].label == "データを再アップロードする"

    # Check the status for main page
    assert len(at.title) == 1
    assert at.title[0].body == "データの可視化📊"
    assert len(at.error) == 0  # Error message should be gone
    assert len(at.header) == 1
    assert at.header[0].body == "指標ごとの比較グラフ"
    assert len(at.selectbox) == 1
    assert at.selectbox[0].label == "比較する指標を選択してください"

    # Check for expander (not natively supported for by Streamlit)
    assert at.main[1].proto.expandable.label == "アップロードされたデータ"
    assert at.main[1].proto.expandable.expanded is False
    assert at.main[2].proto.expandable.label == "関連データ"
    assert at.main[2].proto.expandable.expanded is True


def test_reupload():
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
    # Simulate the user pushing the re-upload button
    at.sidebar.button[0].click().run()
    assert at.session_state["json_obj"] is None
    assert len(at.title) == 1
    assert at.title[0].body == "データの可視化📊"
    assert len(at.error) == 1
    assert (
        at.error[0].body
        == "サイドバーを開き、システムデータをアップロードしてください。"
    )
    # Simulate the user uploading a JSON file again
    at.session_state["json_obj"] = {
        "フェーズ": "ST",
        "システム": "システム１",
        "算出方法": "中央値",
        "テスト仕様書_テストケース数_(予定)": 67.0,
    }
    at.session_state["data_file_name"] = "new_data.json"
    at.session_state["data_file_size"] = 5678
    at.run()

    # Check the status for sidebar
    assert len(at.sidebar) == 1
    assert (
        at.sidebar.success[0].body == "new_data.json (5.7KB) がアップロードされました。"
    )
    assert len(at.sidebar.button) == 1
    assert at.sidebar.button[0].label == "データを再アップロードする"

    # Check the status for main page
    assert len(at.title) == 1
    assert at.title[0].body == "データの可視化📊"
    assert len(at.error) == 0  # Error message should be gone
    assert len(at.header) == 1
    assert at.header[0].body == "指標ごとの比較グラフ"
    assert len(at.selectbox) == 1
    assert at.selectbox[0].label == "比較する指標を選択してください"

    # Check for expander (not natively supported for by Streamlit)
    assert at.main[1].proto.expandable.label == "アップロードされたデータ"
    assert at.main[1].proto.expandable.expanded is False
    assert at.main[2].proto.expandable.label == "関連データ"
    assert at.main[2].proto.expandable.expanded is True
