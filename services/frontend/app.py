"""Streamlit frontend for Insurance Chatbot."""
from __future__ import annotations
import streamlit as st

from core.config import Theme
from core.styles import get_theme_styles
from core.state import init_session_state
from ui.sidebar import render_sidebar
from ui.chat import render_chat_area, handle_user_query
from ui.widgets import render_tips_card, render_suggestions
from ui.panels import render_sources, render_metrics, render_debug_info


def main():
    st.set_page_config(
        page_title="Insurance Chatbot",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    config = render_sidebar()

    st.markdown(get_theme_styles(config.theme), unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="app-header">
            <h1>Insurance Chatbot</h1>
            <p>Asistente para consultas sobre polizas de seguro chilenas</p>
        </div>
    """, unsafe_allow_html=True)

    # Main layout: chat takes priority, suggestions on the side
    col_chat, col_info = st.columns([3, 1])

    with col_chat:
        render_chat_area(config)

    with col_info:
        render_tips_card()
        render_suggestions(lambda s: handle_user_query(s, config))

    # Response panels (sources, metrics, debug) below the chat
    if st.session_state.last_response:
        resp = st.session_state.last_response
        if resp.get("sources"):
            render_sources(resp["sources"])
        if resp.get("usage"):
            render_metrics(resp)
        if config.debug and resp.get("debug"):
            render_debug_info(resp["debug"])


if __name__ == "__main__":
    main()
