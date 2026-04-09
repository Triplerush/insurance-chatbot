import html
from typing import Any, Dict, List
import streamlit as st


def render_sources(sources: List[Dict[str, Any]]) -> None:
    if not sources:
        return

    st.markdown("### Fuentes consultadas")
    for idx, source in enumerate(sources, 1):
        title = source.get("title") or source.get("file_name") or "Documento"
        snippet = (source.get("snippet") or "").strip()
        url = source.get("url")
        page = source.get("page")
        chunk_id = source.get("chunk_id")
        score = source.get("score")

        meta_tags = []
        if page:
            meta_tags.append(f'<span class="source-tag">Pag. {page}</span>')
        if chunk_id is not None:
            meta_tags.append(f'<span class="source-tag">Chunk {chunk_id}</span>')
        if score is not None:
            try:
                meta_tags.append(f'<span class="source-tag">{float(score):.2f}</span>')
            except (ValueError, TypeError):
                pass

        link_html = ""
        if url:
            safe_url = html.escape(url)
            link_html = f'<a href="{safe_url}" target="_blank" rel="noopener" style="color:#667eea;text-decoration:none;font-size:.85rem;">Ver documento</a>'

        safe_title = html.escape(title)
        safe_snippet = html.escape(snippet)

        st.markdown(f"""
            <div class="source-card">
                <div class="source-title">
                    <span class="source-number">{idx}</span>{safe_title}
                </div>
                {f'<div class="source-snippet">{safe_snippet}</div>' if safe_snippet else ''}
                <div class="source-meta">{' '.join(meta_tags)} {link_html}</div>
            </div>
        """, unsafe_allow_html=True)


def render_metrics(response: Dict[str, Any]) -> None:
    usage = response.get("usage", {})
    if not usage:
        return

    metrics = {
        "Documentos recuperados": usage.get("retrieved_documents", 0),
        "Busqueda web": "Activa" if usage.get("web_search_enabled") else "Inactiva",
        "Idioma": usage.get("language", "es").upper(),
        "Top-K": usage.get("top_k", 0),
    }

    st.markdown(
        '<div class="metrics-container">'
        '<h4 style="margin:0 0 .75rem 0;font-size:.95rem;">Metricas de la consulta</h4>',
        unsafe_allow_html=True,
    )
    for label, value in metrics.items():
        st.markdown(f"""
            <div class="metric-item">
                <span class="metric-label">{label}</span>
                <span class="metric-value">{value}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_debug_info(debug_data: Dict[str, Any]) -> None:
    with st.expander("Informacion de Debug", expanded=False):
        st.json(debug_data)
