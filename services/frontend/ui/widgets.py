import streamlit as st
from typing import Callable

SUGGESTIONS = [
    "Que cubre el seguro de incendio?",
    "Cuales son las exclusiones del seguro de vehiculos?",
    "Que incluye la poliza de accidentes personales?",
    "Como funciona el seguro de responsabilidad civil?",
    "Que cubre la asistencia en viaje?",
]


def render_tips_card():
    st.markdown("""
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                    border-radius:12px;padding:1.25rem;color:#fff;margin-bottom:1rem;font-size:.9rem;">
            <strong>Tips para mejores respuestas</strong>
            <ul style="margin:.5rem 0 0 0;padding-left:1.2rem;">
                <li>Se especifico: pregunta sobre coberturas, exclusiones o limites concretos</li>
                <li>Haz preguntas de seguimiento para profundizar</li>
                <li>Activa la busqueda web para informacion actualizada</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


def render_suggestions(on_click: Callable[[str], None]):
    st.markdown("**Preguntas sugeridas**")
    for s in SUGGESTIONS:
        if st.button(s, key=f"sugg_{hash(s)}", use_container_width=True):
            on_click(s)
