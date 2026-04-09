from typing import Any, Dict
from datetime import datetime
import html
import re

import streamlit as st
from core.config import AppConfig
from core.api import call_backend_api
from core.state import format_timestamp


def _md_to_simple_html(text: str) -> str:
    """Minimal markdown-to-HTML for assistant messages (bold, lists, line breaks)."""
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    lines = text.split('\n')
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^[-*]\s', stripped):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            if stripped:
                out.append(f'<p>{stripped}</p>')
    if in_list:
        out.append('</ul>')
    return ''.join(out)


def build_message_html(message: Dict[str, Any], show_timestamp: bool = True) -> str:
    role = message.get("role", "assistant")
    content = message.get("content", "")
    ts_iso = message.get("timestamp")
    ts_txt = ""
    if show_timestamp and ts_iso:
        try:
            ts_txt = format_timestamp(datetime.fromisoformat(ts_iso))
        except Exception:
            ts_txt = ""

    wrapper_cls = "user" if role == "user" else "assistant"
    bubble_cls = "user-message" if role == "user" else "assistant-message"
    ts_html = f"<div class='message-timestamp'>{ts_txt}</div>" if ts_txt else ""

    if role == "user":
        safe_content = html.escape(content)
    else:
        safe_content = _md_to_simple_html(content)

    return (
        f"<div class='message-wrapper {wrapper_cls}'>"
        f"  <div class='message-bubble {bubble_cls}'>"
        f"    <div>{safe_content}</div>"
        f"    {ts_html}"
        f"  </div>"
        f"</div>"
    )


def handle_user_query(text: str, config: AppConfig, chat_placeholder=None) -> None:
    st.session_state.messages.append({
        "role": "user",
        "content": text,
        "timestamp": datetime.now().isoformat()
    })
    st.session_state.total_queries += 1

    if chat_placeholder is not None:
        chat_html = "".join(
            build_message_html(m, config.show_timestamps)
            for m in st.session_state.messages
        )
        chat_placeholder.markdown(
            f'<div class="chat-container">{chat_html}</div>',
            unsafe_allow_html=True,
        )

    response = call_backend_api(
        api_url=config.api_url,
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        top_k=config.top_k,
        enable_web_search=config.enable_web_search,
        debug=config.debug,
        language=config.language,
    )
    st.session_state.last_response = response

    if "error" in response:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["error"],
            "timestamp": datetime.now().isoformat(),
        })
    else:
        answer = response.get("answer", "No se recibió respuesta del servidor.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat(),
        })

    st.rerun()


def render_chat_area(config: AppConfig):
    chat_placeholder = st.empty()

    chat_html = "".join(
        build_message_html(m, config.show_timestamps)
        for m in st.session_state.messages
    )
    chat_placeholder.markdown(
        f'<div class="chat-container">{chat_html}</div>',
        unsafe_allow_html=True,
    )

    prompt = st.chat_input("Escribe tu consulta sobre seguros...")
    if prompt:
        handle_user_query(prompt, config, chat_placeholder)
