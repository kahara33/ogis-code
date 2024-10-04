import streamlit as st

from app_util.common import COMMON_PAGE_CONFIG, HOME_MARKDOWN, init_session_state
from app_util.sidebar import sidebar0

# 1. Set the page configuration.
st.set_page_config(
    page_title="ホーム",
    page_icon="🏠",
    **COMMON_PAGE_CONFIG,  # type: ignore[arg-type]
)

# 2. Initialize session state variables.
init_session_state()

# 3. Render the sidebar.
sidebar0()

# 4. Render the main content.
st.title("機能紹介🏠")
st.markdown(HOME_MARKDOWN)
