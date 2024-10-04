import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from app_util.common import COMMON_PAGE_CONFIG, init_session_state
from app_util.sidebar import error1, sidebar1
from orchestrator.review import get_pre_info
from rag_tabular.json_to_db import query_sql_db

mpl.rcParams["font.family"] = "Arial Unicode MS"
custom_red = (211 / 255, 45 / 255, 64 / 255)  # Ogis R:211, G:45, B:64
custom_blue = (37 / 255, 90 / 255, 166 / 255)  # Ogis R:37, G:90, B:166


# 1. Set the page configuration.
st.set_page_config(
    page_title="可視化",
    page_icon="📊",
    **COMMON_PAGE_CONFIG,  # type: ignore[arg-type]
)

# 2. Initialize session state variables.
init_session_state()

# 3. Render the sidebar.
sidebar1()

# 4. Render the main content.
st.title("データの可視化📊")
error1()

if (json_obj := st.session_state["json_obj"]) is not None:
    with st.expander("アップロードされたデータ", expanded=False):
        st.write(json_obj)
    series, df = query_sql_db(json_obj)

    if "算出方法" in df.columns:
        df.drop(
            columns=["算出方法"], inplace=True
        )  # TODO: Do not hardcode the column name
    if "分類" in df.columns:
        df.drop(columns=["分類"], inplace=True)  # TODO: Do not hardcode the column name
    df.set_index("システム", inplace=True)  # TODO: Do not hardcode the column name
    df = df.T

    with st.expander("関連データ", expanded=True):
        st.dataframe(df)

    _, df_for_graph, reference_information = get_pre_info(
        json_obj=json_obj, bool_current_system=False
    )

    if "算出方法" in df_for_graph.columns:
        df_for_graph.drop(
            columns=["算出方法"], inplace=True
        )  # TODO: Do not hardcode the column name
    if "分類" in df_for_graph.columns:
        df_for_graph.drop(
            columns=["分類"], inplace=True
        )  # TODO: Do not hardcode the column name
    df_for_graph.set_index(
        "システム", inplace=True
    )  # TODO: Do not hardcode the column name
    df_for_graph = df_for_graph.T

    st.header("指標ごとの比較グラフ")
    exclude_columns = [
        "フェーズ",
        "システム",
        "算出方法",
        "分類",
    ]  # TODO: Do not hardcode the column name
    selectable_columns = [col for col in json_obj.keys() if col not in exclude_columns]
    selected_column = st.selectbox("比較する指標を選択してください", selectable_columns)

    if selected_column in df_for_graph.index:
        # 現在のシステムと過去のシステムのデータを取得
        current_system = json_obj["システム"]
        if current_system in df_for_graph.columns:
            current_value = df_for_graph.loc[selected_column, current_system]
            past_systems = [
                sys for sys in df_for_graph.columns if sys != current_system
            ]
            past_values = df_for_graph.loc[selected_column, past_systems].tolist()

            # 棒グラフを表示
            chart_data = {
                "システム": [current_system] + past_systems,
                "値": [current_value] + past_values,
            }
            chart_df_for_graph = pd.DataFrame(chart_data)
            chart_df_for_graph.set_index("システム", inplace=True)

            # 現在のデータの色を変更
            current_index = chart_df_for_graph.index.tolist().index(current_system)
            colors = [custom_blue] * len(chart_df_for_graph)
            colors[current_index] = custom_red

            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.barh(
                chart_df_for_graph.index, chart_df_for_graph["値"], color=colors
            )
            ax.set_yticks(chart_df_for_graph.index)
            ax.set_yticklabels(chart_df_for_graph.index, ha="right")
            ax.invert_yaxis()
            ax.bar_label(
                bars,
                labels=[f"{val:.2f}" for val in chart_df_for_graph["値"]],
                padding=5,
            )
            st.pyplot(fig)
        else:
            st.warning(f"現在のシステム '{current_system}' のデータが見つかりません。")
    else:
        st.warning(f"選択された項目 '{selected_column}' のデータが見つかりません。")

    # st.scatter_chart(df)
