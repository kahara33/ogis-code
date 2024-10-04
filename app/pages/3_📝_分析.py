import streamlit as st

from app_util.common import ANALYSIS_PROMPT, COMMON_PAGE_CONFIG, init_session_state
from app_util.sidebar import error3, sidebar3
from orchestrator.review import generate_review, get_pre_info, review_agent


def is_ready_for_analysis() -> bool:
    return (
        st.session_state["json_obj"] is not None and st.session_state["api"] is not None
    )


def has_started_analysis() -> bool:
    return st.session_state["started_analysis"]


# 1. Set the page configuration.
st.set_page_config(
    page_title="分析",
    page_icon="📝",
    **COMMON_PAGE_CONFIG,  # type: ignore[arg-type]
)

# 2. Initialize session state variables.
init_session_state()
if "review_messages" not in st.session_state:
    st.session_state["review_messages"] = []
if "analysis_prompt" not in st.session_state:
    st.session_state["analysis_prompt"] = ANALYSIS_PROMPT
if "started_analysis" not in st.session_state:
    st.session_state["started_analysis"] = False
if "review_text" not in st.session_state:
    st.session_state["review_text"] = ""

# 3. Render the sidebar.
sidebar3()

# 4. Render the main content.
st.title("インタラクティブな分析📝")
error3()


if is_ready_for_analysis() and has_started_analysis():
    with st.expander("分析観点", expanded=True):
        st.markdown(st.session_state["analysis_prompt"])
else:
    st.text_area(
        "分析観点についてのプロンプトを編集できます",
        value=st.session_state["analysis_prompt"],
        height=400,  # TODO: Do not hardcode the height
        max_chars=None,
        key="_analysis_prompt",
        help="分析の指示を入力してください。",
        on_change=lambda: st.session_state.update(
            {"analysis_prompt": st.session_state._analysis_prompt}
        ),
        placeholder=None,
        disabled=False,
        label_visibility="visible",
    )

if (json_obj := st.session_state["json_obj"]) is not None:
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
    with st.expander("関連データ", expanded=False):
        st.dataframe(df_for_graph)

    # IPA参照情報を表示
    if reference_information:
        with st.expander("IPA参照情報", expanded=False):
            st.markdown("---")
            for info in reference_information:
                page_number = info["page_number"]
                page_content = info["page_content"]

                # ページ番号とページコンテンツをMarkdown形式で表示
                st.markdown(f"p. {page_number} {page_content}")
                st.markdown("---")

if is_ready_for_analysis() and not has_started_analysis():
    st.button(
        "分析を開始する",
        key="_started_analysis",
        help="分析観点のプロンプトに従って、入力されたデータを分析します。",
        on_click=lambda: st.session_state.update(
            {
                "started_analysis": True,
                "review_messages": [],
                "review_text": "",
            }
        ),
        type="primary",
        disabled=False,
        use_container_width=False,
    )

if is_ready_for_analysis() and has_started_analysis():
    if not st.session_state["review_messages"]:
        stream, prompt_content = generate_review(
            st.session_state["json_obj"],
            st.session_state["analysis_prompt"],
            st.session_state["api"],
        )
        st.session_state["review_messages"].append(
            {"role": "user", "content": prompt_content}
        )
        review_result_area = st.empty()
        review_text = ""
        for chunk in stream:
            review_text += chunk
            review_result_area.markdown(review_text)
        st.markdown("---")
        st.session_state["review_text"] = review_text
        st.session_state["review_messages"].append(
            {"role": "assistant", "content": review_text}
        )
    else:
        st.markdown(st.session_state["review_text"])
        st.markdown("---")

if (
    is_ready_for_analysis()
    and st.session_state["started_analysis"]
    and st.session_state["api"] is not None
):
    for message in st.session_state["review_messages"][2:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("メッセージを入力")
    if prompt:
        st.session_state["review_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = review_agent(
                [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["review_messages"]
                ],
                st.session_state["api"],
            )
            chat_area = st.empty()
            response = ""
            for chunk in stream:
                if (
                    len(chunk.choices) > 0
                    and hasattr(chunk.choices[0].delta, "content")
                    and chunk.choices[0].delta.content is not None
                ):
                    content = chunk.choices[0].delta.content
                    response += content
                    chat_area.markdown(response, unsafe_allow_html=True)
            st.session_state["review_messages"].append(
                {"role": "assistant", "content": response}
            )
        print("message:\n", st.session_state["review_messages"])
