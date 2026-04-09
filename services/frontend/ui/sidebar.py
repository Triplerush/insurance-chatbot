import streamlit as st
from core.api import check_api_status, DEFAULT_API_URL
from core.config import AppConfig, Theme


def render_sidebar() -> AppConfig:
    st.sidebar.markdown("## Configuracion")

    # API status
    if check_api_status(DEFAULT_API_URL):
        st.sidebar.markdown(
            '<div class="status-indicator status-online">API Online</div>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<div class="status-indicator status-error">API Offline</div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("---")

    # Search settings
    st.sidebar.markdown("### Busqueda")
    top_k = st.sidebar.slider("Documentos a recuperar", 1, 10, 4)
    enable_web_search = st.sidebar.checkbox("Habilitar busqueda web", value=False)

    st.sidebar.markdown("---")

    # Display settings
    st.sidebar.markdown("### Interfaz")
    theme = st.sidebar.selectbox(
        "Tema",
        options=[Theme.DARK, Theme.LIGHT],
        format_func=lambda x: "Claro" if x == Theme.LIGHT else "Oscuro",
    )
    language = st.sidebar.selectbox(
        "Idioma de respuesta",
        options=["es", "en"],
        format_func=lambda x: "Espanol" if x == "es" else "English",
    )
    show_timestamps = st.sidebar.checkbox("Mostrar timestamps", value=True)

    st.sidebar.markdown("---")

    # Advanced
    with st.sidebar.expander("Opciones avanzadas"):
        debug = st.checkbox("Modo Debug", value=False)

    st.sidebar.markdown("---")

    # Clear conversation
    if st.sidebar.button("Limpiar conversacion", use_container_width=True):
        st.session_state.messages = st.session_state.messages[:1]
        st.session_state.last_response = None
        st.session_state.total_queries = 0
        st.rerun()

    return AppConfig(
        api_url=DEFAULT_API_URL.rstrip("/"),
        top_k=top_k,
        enable_web_search=enable_web_search,
        debug=debug,
        language=language,
        theme=theme,
        auto_scroll=False,
        show_timestamps=show_timestamps,
    )
