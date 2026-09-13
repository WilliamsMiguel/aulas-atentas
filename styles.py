"""
Módulo de Estilos y Componentes UI para Aulas Atentas.
Ofrece un diseño dashboard profesional, moderno, innovador e interactivo con soporte para Modo Oscuro y Claro.
"""

import streamlit as st

def get_css(theme="dark"):
    """
    Retorna las reglas CSS adaptadas según el tema seleccionado ('dark' o 'light').
    """
    is_dark = theme == "dark"
    
    bg_main = "#0B1220" if is_dark else "#F1F5F9"
    bg_sec = "#111827" if is_dark else "#FFFFFF"
    bg_card = "#172033" if is_dark else "#FFFFFF"
    border_color = "#263449" if is_dark else "#CBD5E1"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#475569"
    
    cyan = "#38BDF8" if is_dark else "#0284C7"
    violet = "#8B5CF6" if is_dark else "#7C3AED"
    green = "#22C55E" if is_dark else "#16A34A"
    yellow = "#F59E0B" if is_dark else "#D97706"
    red = "#EF4444" if is_dark else "#DC2626"
    
    card_shadow = "0 8px 30px rgba(0, 0, 0, 0.35)" if is_dark else "0 4px 20px rgba(15, 23, 42, 0.08)"
    hover_shadow = "0 12px 40px rgba(56, 189, 248, 0.15)" if is_dark else "0 8px 25px rgba(2, 132, 199, 0.12)"
    hero_bg = "linear-gradient(135deg, #111827 0%, #172033 60%, #1E293B 100%)" if is_dark else "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 60%, #E2E8F0 100%)"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {bg_sec} !important;
        border-right: 1px solid {border_color} !important;
    }}
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: {text_primary} !important;
        font-weight: 700;
    }}

    /* Hero Banner */
    .hero-banner {{
        background: {hero_bg};
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}

    .hero-banner::before {{
        content: '';
        position: absolute;
        top: -60px;
        right: -40px;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, {cyan}20 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }}

    .hero-header-row {{
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 10px;
    }}

    .hero-icon-box {{
        width: 60px;
        height: 60px;
        border-radius: 16px;
        background: linear-gradient(135deg, {cyan}20, {violet}30);
        border: 1px solid {cyan}40;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        box-shadow: 0 4px 15px {cyan}25;
    }}

    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {text_primary};
        margin: 0;
        line-height: 1.1;
    }}

    .hero-subtitle {{
        font-size: 1.1rem;
        color: {cyan};
        font-weight: 600;
        margin-top: 4px;
        margin-bottom: 12px;
    }}

    .hero-desc {{
        font-size: 0.95rem;
        color: {text_secondary};
        line-height: 1.6;
        margin-bottom: 18px;
        max-width: 900px;
    }}

    .status-badge-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: center;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: {bg_card};
        border: 1px solid {border_color};
        color: {text_primary};
    }}

    .status-pill-active {{
        border-color: {green}60;
        color: {green};
        background: {green}15;
    }}

    .status-pill-info {{
        border-color: {cyan}60;
        color: {cyan};
        background: {cyan}15;
    }}

    .pulse-dot {{
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: {green};
        box-shadow: 0 0 10px {green};
        animation: pulse-animation 1.8s infinite;
    }}

    @keyframes pulse-animation {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {green}70; }}
        70% {{ transform: scale(1.15); box-shadow: 0 0 0 9px rgba(34, 197, 94, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
    }}

    /* Custom Container Card */
    .custom-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
        transition: all 0.25s ease;
    }}

    .custom-card:hover {{
        border-color: {cyan}50;
        box-shadow: {hover_shadow};
    }}

    /* Specific Model Card Headers */
    .model-card-fatigue {{
        border-top: 4px solid {violet};
    }}

    .model-card-postures {{
        border-top: 4px solid {cyan};
    }}

    .model-card-attention {{
        border-top: 4px solid {green};
    }}

    .card-title-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid {border_color};
    }}

    .card-title-text {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {text_primary};
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .card-metrics-row {{
        display: flex;
        gap: 12px;
        align-items: center;
    }}

    .metric-badge {{
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 8px;
        background: {bg_sec};
        border: 1px solid {border_color};
        color: {text_secondary};
    }}

    /* Mode Info Cards */
    .mode-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }}

    .warning-card {{
        background: {yellow}12;
        border: 1px solid {yellow}40;
        border-radius: 12px;
        padding: 14px 18px;
        color: {yellow};
        font-size: 0.88rem;
        font-weight: 500;
        margin-top: 12px;
    }}

    /* Image Preview Cards */
    .img-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: {card_shadow};
    }}

    .img-card-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Table & Detection Badges */
    .empty-state-card {{
        text-align: center;
        padding: 36px 20px;
        background: {bg_card};
        border: 1px dashed {border_color};
        border-radius: 14px;
        color: {text_secondary};
        font-size: 0.98rem;
        margin: 16px 0;
    }}

    .class-pill {{
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        background: {cyan}15;
        color: {cyan};
        border: 1px solid {cyan}30;
    }}

    /* Streamlit Input Overrides */
    .stRadio > label, .stSlider > label, .stSelectbox > label, .stCheckbox > label {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {bg_card} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
    }}

    [data-testid="stFileUploader"] {{
        background-color: {bg_card} !important;
        border: 2px dashed {cyan}50 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: all 0.3s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: {cyan} !important;
        box-shadow: {hover_shadow} !important;
    }}

    </style>
    """

def render_header(num_modelos=3, tema="dark"):
    """Renderiza el encabezado principal con badge de estado e indicadores."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-header-row">
                <div class="hero-icon-box">👁️</div>
                <div>
                    <h1 class="hero-title">Aulas Atentas</h1>
                    <div class="hero-subtitle">Sistema inteligente de detección de fatiga, posturas y atención estudiantil</div>
                </div>
            </div>
            <div class="hero-desc">
                Analiza imágenes o video en vivo mediante modelos YOLOv8 entrenados para apoyar el monitoreo del comportamiento estudiantil.
            </div>
            <div class="status-badge-container">
                <div class="status-pill status-pill-active">
                    <span class="pulse-dot"></span>
                    <span>Sistema operativo</span>
                </div>
                <div class="status-pill status-pill-info">
                    <span>⚡ YOLOv8 AI Engine</span>
                </div>
                <div class="status-pill">
                    <span>📦 {num_modelos} modelos cargados</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_empty_detections():
    """Renderiza la tarjeta informativa cuando no hay detecciones."""
    st.markdown(
        """
        <div class="empty-state-card">
            🔍 <b>No se encontraron detecciones con la confianza seleccionada.</b><br/>
            <span style="font-size: 0.88rem; opacity: 0.8;">Prueba ajustando el nivel mínimo de confianza en el panel lateral.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
