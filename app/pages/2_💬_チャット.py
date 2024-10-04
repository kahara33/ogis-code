import streamlit as st
from langchain_core.messages import ChatMessage

from app_util.common import COMMON_PAGE_CONFIG, init_session_state
from app_util.sidebar import error2, sidebar2
from util.api import APIType

# 1. Set the page configuration.
st.set_page_config(
    page_title="チャット",
    page_icon="💬",
    **COMMON_PAGE_CONFIG,  # type: ignore[arg-type]
)

# 2. Initialize session state variables.
init_session_state()
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# 3. Render the sidebar.
sidebar2()

# 4. Render the main content.
st.title("AIとのチャット💬")
error2()

for message in st.session_state["chat_messages"]:
    with st.chat_message(message.role):
        st.markdown(message.content)

if st.session_state["api"] is not None:

    if prompt := st.chat_input("メッセージを入力"):
        st.session_state["chat_messages"].append(
            ChatMessage(prompt, role="user")  # type: ignore[misc]
        )
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_model = st.session_state["api"].init_chat_model()
        stream = chat_model.stream(st.session_state["chat_messages"])
        # Skip the first chunk with no content
        if st.session_state["api"].type is APIType.AZURE_OPENAI:
            next(stream)
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state["chat_messages"].append(
            ChatMessage(response, role="assistant")  # type: ignore[misc]
        )
