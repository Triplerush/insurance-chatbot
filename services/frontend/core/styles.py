from .config import Theme

# Palette constants to avoid repetition
_PRIMARY = "#667eea"
_SECONDARY = "#764ba2"
_GRADIENT = f"linear-gradient(135deg,{_PRIMARY} 0%,{_SECONDARY} 100%)"


def get_theme_styles(theme: Theme) -> str:
    base = f"""
    <style>
    .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, #0F172A 0%, #111827 100%) !important;
        color: #E2E8F0 !important;
    }}

    /* Header */
    .app-header {{
        background: {_GRADIENT};
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(102,126,234,.25);
        color: white;
        text-align: center;
    }}
    .app-header h1 {{
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -.5px;
    }}
    .app-header p {{
        margin-top: .35rem;
        opacity: .9;
        font-size: 1rem;
    }}

    /* Chat */
    .chat-container {{
        background: linear-gradient(180deg, #FCFEFF 0%, #F3F6FA 100%);
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(2,6,23,.05);
        min-height: 420px;
        margin-bottom: 1rem;
        color: #0B1220;
    }}
    .message-wrapper {{
        display: flex;
        margin-bottom: 1rem;
        animation: fadeInUp .3s ease;
    }}
    .message-wrapper.assistant {{ justify-content: flex-start; }}
    .message-wrapper.user {{ justify-content: flex-end; }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .message-bubble {{
        display: inline-block;
        padding: .85rem 1.15rem;
        border-radius: 16px;
        font-size: .95rem;
        line-height: 1.6;
        word-wrap: break-word;
        max-width: 85%;
    }}
    .user-message {{
        background: #fff;
        color: #1a202c;
        border: 1.5px solid {_PRIMARY};
        box-shadow: 0 2px 8px rgba(102,126,234,.1);
    }}
    .assistant-message {{
        background: {_GRADIENT};
        color: #fff;
        box-shadow: 0 2px 12px rgba(102,126,234,.2);
    }}
    /* Markdown inside assistant bubbles */
    .assistant-message p {{ margin: 0 0 .5rem 0; }}
    .assistant-message p:last-child {{ margin-bottom: 0; }}
    .assistant-message ul, .assistant-message ol {{
        margin: .25rem 0 .5rem 1.2rem;
        padding: 0;
    }}
    .assistant-message strong {{ font-weight: 600; }}

    .message-timestamp {{
        display: block;
        margin-top: .3rem;
        font-size: .72rem;
        line-height: 1;
        opacity: .7;
    }}
    .message-wrapper.user .message-timestamp {{ color: #718096; }}
    .message-wrapper.assistant .message-timestamp {{ color: #E2E8F0; }}

    /* Sources */
    .source-card {{
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: .75rem;
        transition: all .2s ease;
        position: relative;
        overflow: hidden;
    }}
    .source-card:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(0,0,0,.08);
        border-color: {_PRIMARY};
    }}
    .source-card::before {{
        content: '';
        position: absolute;
        left: 0; top: 0;
        height: 100%; width: 3px;
        background: {_GRADIENT};
    }}
    .source-number {{
        display: inline-block;
        background: {_GRADIENT};
        color: #fff;
        width: 22px; height: 22px;
        border-radius: 50%;
        text-align: center;
        line-height: 22px;
        font-size: .8rem;
        font-weight: 600;
        margin-right: .4rem;
    }}
    .source-title {{
        font-weight: 600;
        color: #2d3748;
        font-size: .95rem;
    }}
    .source-snippet {{
        color: #4a5568;
        font-size: .88rem;
        line-height: 1.55;
        margin: .5rem 0;
        padding: .6rem .75rem;
        background: #f7fafc;
        border-radius: 8px;
        border-left: 3px solid {_PRIMARY};
    }}
    .source-meta {{
        display: flex;
        gap: .5rem;
        align-items: center;
        flex-wrap: wrap;
    }}
    .source-tag {{
        display: inline-block;
        background: #eef2ff;
        color: {_PRIMARY};
        padding: .2rem .6rem;
        border-radius: 999px;
        font-size: .72rem;
        font-weight: 500;
    }}

    /* Metrics */
    .metrics-container {{
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }}
    .metric-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: .6rem .75rem;
        background: #fff;
        border-radius: 8px;
        margin-bottom: .5rem;
        border: 1px solid #e2e8f0;
    }}
    .metric-label {{ color: #718096; font-size: .82rem; font-weight: 500; }}
    .metric-value {{
        color: #2d3748;
        font-weight: 700;
        font-size: 1rem;
        background: {_GRADIENT};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Typing */
    .typing-indicator {{
        display: inline-flex;
        align-items: center;
        padding: .75rem;
        gap: .35rem;
    }}
    .typing-dot {{
        width: 7px; height: 7px;
        background: {_PRIMARY};
        border-radius: 50%;
        animation: typingAnim 1.4s infinite;
    }}
    .typing-dot:nth-child(2) {{ animation-delay: .2s; }}
    .typing-dot:nth-child(3) {{ animation-delay: .4s; }}
    @keyframes typingAnim {{
        0%,60%,100% {{ transform: translateY(0); opacity: .5; }}
        30% {{ transform: translateY(-8px); opacity: 1; }}
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }}
    section[data-testid="stSidebar"] .stButton>button {{
        background: {_GRADIENT};
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: .5rem 1rem;
        font-weight: 500;
        transition: all .2s ease;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102,126,234,.35);
    }}

    .status-indicator {{
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .4rem .8rem;
        border-radius: 999px;
        font-size: .85rem;
        font-weight: 500;
    }}
    .status-online {{ background: rgba(16,185,129,.1); color: #10b981; border: 1px solid #10b981; }}
    .status-error {{ background: rgba(239,68,68,.1); color: #ef4444; border: 1px solid #ef4444; }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: #f1f5f9; border-radius: 10px; }}
    ::-webkit-scrollbar-thumb {{ background: {_GRADIENT}; border-radius: 10px; }}
    </style>
    """
    dark = f"""
    <style>
    .chat-container {{ background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border-color: #334155; }}
    .user-message {{ background: #1e293b; color: #f1f5f9; border-color: {_PRIMARY}; }}
    .message-wrapper.user .message-timestamp {{ color: #94a3b8; }}
    .source-card {{ background: #1e293b; border-color: #334155; color: #e2e8f0; }}
    .source-title {{ color: #e2e8f0; }}
    .source-snippet {{ background: #0f172a; color: #cbd5e1; }}
    .source-tag {{ background: rgba(102,126,234,.15); }}
    .metrics-container {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-color: #334155; }}
    .metric-item {{ background: #0f172a; border-color: #334155; }}
    .metric-label {{ color: #94a3b8; }}
    </style>
    """
    return base + (dark if theme == Theme.DARK else "")
