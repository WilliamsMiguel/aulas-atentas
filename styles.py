"""
Módulo de estilos para Aulas Atentas.
Sistema de diseño premium con soporte de tema oscuro y claro.
"""

import streamlit as st


# ──────────────────────────────────────────────────────────────────────────────
# PALETA DE COLORES POR TEMA
# ──────────────────────────────────────────────────────────────────────────────

def _palette(theme: str) -> dict:
    """Retorna el diccionario de colores según el tema activo."""
    dark = theme == "dark"
    return {
        "bg_main":      "#070B14" if dark else "#F1F5F9",
        "bg_sec":       "#0D1424" if dark else "#E2E8F0",
        "bg_card":      "#111B2E" if dark else "#FFFFFF",
        "bg_elevated":  "#17243A" if dark else "#FFFFFF",
        "border":       "#263853" if dark else "#CBD5E1",
        "text_primary": "#F8FAFC" if dark else "#0F172A",
        "text_sec":     "#94A3B8" if dark else "#475569",
        "cyan":         "#38BDF8" if dark else "#0284C7",
        "blue":         "#60A5FA" if dark else "#2563EB",
        "violet":       "#8B5CF6" if dark else "#7C3AED",
        "green":        "#22C55E" if dark else "#16A34A",
        "yellow":       "#F59E0B" if dark else "#D97706",
        "red":          "#EF4444" if dark else "#DC2626",
        "card_shadow":  "0 8px 32px rgba(0,0,0,0.45)" if dark else "0 4px 20px rgba(15,23,42,0.09)",
        "hover_shadow": "0 12px 40px rgba(56,189,248,0.12)" if dark else "0 8px 24px rgba(2,132,199,0.10)",
        "hero_bg":      "linear-gradient(135deg,#0D1424 0%,#111B2E 60%,#17243A 100%)" if dark else "linear-gradient(135deg,#FFFFFF 0%,#F8FAFC 60%,#E2E8F0 100%)",
        "grid_opacity": "0.035" if dark else "0.06",
        "glow_opacity": "0.18" if dark else "0.10",
        "is_dark":      dark,
    }


# ──────────────────────────────────────────────────────────────────────────────
# CSS PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

def get_css(theme: str = "dark") -> str:
    """
    Retorna el bloque <style> completo adaptado al tema.
    Incluye: tipografía, paleta, fondo animado, tarjetas, responsive, accesibilidad.
    """
    p = _palette(theme)

    return f"""
    <style>
    /* ── FUENTE ────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── RESET Y BASE ──────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                     BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: {p['bg_main']} !important;
        color: {p['text_primary']} !important;
        -webkit-font-smoothing: antialiased;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
        border-bottom: none !important;
    }}

    /* ── FONDO ANIMADO ─────────────────────────────────────────────── */
    /* Capa de rejilla tecnológica */
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient({p['border']}40 1px, transparent 1px),
            linear-gradient(90deg, {p['border']}40 1px, transparent 1px);
        background-size: 48px 48px;
        opacity: {p['grid_opacity']};
        pointer-events: none;
        z-index: 0;
        animation: gridShift 60s linear infinite;
    }}

    /* Luz radial ambiental – esquina superior derecha */
    [data-testid="stAppViewContainer"]::after {{
        content: '';
        position: fixed;
        top: -180px;
        right: -120px;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle, {p['cyan']}22 0%, {p['blue']}10 40%, transparent 70%);
        opacity: {p['glow_opacity']};
        pointer-events: none;
        z-index: 0;
        animation: ambientPulse 12s ease-in-out infinite;
    }}

    /* Luz radial secundaria – esquina inferior izquierda */
    [data-testid="stMain"]::before {{
        content: '';
        position: fixed;
        bottom: -150px;
        left: -100px;
        width: 480px;
        height: 480px;
        border-radius: 50%;
        background: radial-gradient(circle, {p['violet']}18 0%, transparent 65%);
        opacity: {p['glow_opacity']};
        pointer-events: none;
        z-index: 0;
        animation: ambientPulse 16s ease-in-out infinite reverse;
    }}

    @keyframes gridShift {{
        0%   {{ background-position: 0 0, 0 0; }}
        100% {{ background-position: 48px 48px, 48px 48px; }}
    }}

    @keyframes ambientPulse {{
        0%, 100% {{ transform: scale(1);   opacity: {p['glow_opacity']}; }}
        50%       {{ transform: scale(1.15); opacity: calc({p['glow_opacity']} * 1.6); }}
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(16px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulseStatus {{
        0%, 100% {{ box-shadow: 0 0 0 0 {p['green']}55; }}
        60%       {{ box-shadow: 0 0 0 8px {p['green']}00; }}
    }}

    @keyframes shimmer {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}

    /* ── ACCESIBILIDAD — MOVIMIENTO REDUCIDO ───────────────────────── */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    /* ── SIDEBAR ───────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background-color: {p['bg_sec']} !important;
        border-right: 1px solid {p['border']} !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {p['text_primary']} !important;
        font-weight: 700;
        letter-spacing: -0.01em;
    }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {{
        color: {p['text_sec']} !important;
        font-size: 0.875rem;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: {p['border']} !important;
        opacity: 0.6;
    }}

    /* Sidebar section label */
    .sidebar-section-label {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {p['text_sec']};
        padding: 4px 0 8px;
        border-bottom: 1px solid {p['border']};
        margin-bottom: 12px;
    }}

    /* Sidebar status block */
    .sidebar-status-block {{
        background: {p['bg_card']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 8px;
    }}

    .sidebar-status-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        padding: 3px 0;
        color: {p['text_sec']};
    }}

    .sidebar-status-value {{
        font-weight: 600;
        color: {p['text_primary']};
        font-size: 0.8rem;
    }}

    /* ── HERO BANNER ───────────────────────────────────────────────── */
    .hero-banner {{
        background: {p['hero_bg']};
        border: 1px solid {p['border']};
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 28px;
        box-shadow: {p['card_shadow']};
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease-out both;
    }}

    /* Línea de acento superior */
    .hero-banner::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {p['cyan']}, {p['violet']}, {p['blue']});
        border-radius: 20px 20px 0 0;
    }}

    .hero-title {{
        font-size: clamp(28px, 4vw, 44px);
        font-weight: 800;
        letter-spacing: -0.03em;
        color: {p['text_primary']};
        margin: 0 0 4px;
        line-height: 1.1;
    }}

    .hero-title span {{
        background: linear-gradient(135deg, {p['cyan']}, {p['blue']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    .hero-subtitle {{
        font-size: 1rem;
        color: {p['text_sec']};
        font-weight: 400;
        margin: 0 0 20px;
        max-width: 640px;
        line-height: 1.55;
    }}

    .hero-pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
    }}

    /* ── STATUS PILLS ──────────────────────────────────────────────── */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: {p['bg_card']};
        border: 1px solid {p['border']};
        color: {p['text_primary']};
        letter-spacing: 0.01em;
    }}

    .status-pill-active {{
        border-color: {p['green']}55;
        color: {p['green']};
        background: {p['green']}12;
    }}

    .status-pill-info {{
        border-color: {p['cyan']}50;
        color: {p['cyan']};
        background: {p['cyan']}10;
    }}

    .status-pill-warn {{
        border-color: {p['yellow']}50;
        color: {p['yellow']};
        background: {p['yellow']}10;
    }}

    /* Punto de estado CSS puro (sin emojis) */
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }}

    .status-dot-green {{
        background: {p['green']};
        animation: pulseStatus 2s ease-in-out infinite;
    }}

    .status-dot-cyan  {{ background: {p['cyan']}; }}
    .status-dot-yellow{{ background: {p['yellow']}; }}
    .status-dot-red   {{ background: {p['red']}; }}
    .status-dot-violet{{ background: {p['violet']}; }}

    /* ── TARJETAS PRINCIPALES ──────────────────────────────────────── */
    .custom-card {{
        background: {p['bg_card']};
        border: 1px solid {p['border']};
        border-radius: 18px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: {p['card_shadow']};
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        animation: fadeInUp 0.4s ease-out both;
    }}

    .custom-card:hover {{
        border-color: {p['cyan']}45;
        box-shadow: {p['hover_shadow']};
    }}

    /* Tarjeta de modelo — Fatiga */
    .model-card-fatigue {{
        border-top: 3px solid {p['violet']};
    }}

    /* Tarjeta de modelo — Posturas */
    .model-card-postures {{
        border-top: 3px solid {p['cyan']};
    }}

    /* Tarjeta de modelo — Atención */
    .model-card-attention {{
        border-top: 3px solid {p['green']};
    }}

    .card-title-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid {p['border']};
        flex-wrap: wrap;
        gap: 10px;
    }}

    .card-title-text {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {p['text_primary']};
        letter-spacing: -0.01em;
    }}

    /* ── TARJETA DE AVISO ──────────────────────────────────────────── */
    .warning-card {{
        background: {p['yellow']}0D;
        border: 1px solid {p['yellow']}35;
        border-left: 3px solid {p['yellow']};
        border-radius: 12px;
        padding: 13px 18px;
        color: {p['yellow']};
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 16px;
        line-height: 1.5;
    }}

    /* Tarjeta de información (azul) */
    .info-card {{
        background: {p['cyan']}0D;
        border: 1px solid {p['cyan']}30;
        border-left: 3px solid {p['cyan']};
        border-radius: 12px;
        padding: 13px 18px;
        color: {p['cyan']};
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 16px;
        line-height: 1.5;
    }}

    /* ── DROPZONE DE IMAGEN ────────────────────────────────────────── */
    .dropzone-card {{
        background: {p['bg_card']};
        border: 2px dashed {p['border']};
        border-radius: 16px;
        padding: 48px 24px;
        text-align: center;
        transition: border-color 0.2s ease, background 0.2s ease;
        margin: 8px 0 16px;
    }}

    .dropzone-card:hover {{
        border-color: {p['cyan']}70;
        background: {p['cyan']}06;
    }}

    .dropzone-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {p['text_primary']};
        margin-bottom: 6px;
    }}

    .dropzone-subtitle {{
        font-size: 0.85rem;
        color: {p['text_sec']};
        line-height: 1.5;
    }}

    /* ── TARJETAS DE IMAGEN ────────────────────────────────────────── */
    .img-card {{
        background: {p['bg_card']};
        border: 1px solid {p['border']};
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: {p['card_shadow']};
        animation: fadeInUp 0.35s ease-out both;
    }}

    .img-card-title {{
        font-size: 0.9rem;
        font-weight: 700;
        color: {p['text_primary']};
        margin-bottom: 10px;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        font-size: 0.75rem;
        color: {p['text_sec']};
    }}

    /* ── ESTADO VACÍO ──────────────────────────────────────────────── */
    .empty-state-card {{
        text-align: center;
        padding: 36px 20px;
        background: {p['bg_card']};
        border: 1px dashed {p['border']};
        border-radius: 14px;
        color: {p['text_sec']};
        font-size: 0.9rem;
        margin: 14px 0;
        line-height: 1.6;
    }}

    .empty-state-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {p['text_primary']};
        margin-bottom: 6px;
    }}

    /* ── PILLS DE CLASES DETECTADAS ────────────────────────────────── */
    .class-pill {{
        display: inline-block;
        padding: 3px 10px;
        margin: 3px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        background: {p['cyan']}14;
        color: {p['cyan']};
        border: 1px solid {p['cyan']}28;
        letter-spacing: 0.01em;
    }}

    /* ── GRILLA DE INFO DE CÁMARA ──────────────────────────────────── */
    .camera-info-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px;
        margin-top: 16px;
        margin-bottom: 18px;
    }}

    .camera-info-item {{
        background: {p['bg_elevated']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 11px 14px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        transition: border-color 0.2s ease;
    }}

    .camera-info-item:hover {{
        border-color: {p['cyan']}40;
    }}

    .camera-info-label {{
        font-size: 0.68rem;
        font-weight: 700;
        color: {p['text_sec']};
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }}

    .camera-info-value {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {p['text_primary']};
        word-break: break-word;
    }}

    /* ── WEBRTC — CÁMARA ───────────────────────────────────────────── */
    /* Ocultar el botón SELECT DEVICE del componente streamlit-webrtc */
    div[data-testid="stWebrtc"] button[kind="secondary"],
    div[data-testid="stWebrtc"] select {{
        display: none !important;
    }}

    /* Video nítido, sin filtros visuales */
    div[data-testid="stWebrtc"] video,
    div[data-testid="stWebrtc"] canvas {{
        width: 100% !important;
        height: auto !important;
        max-width: 100% !important;
        border-radius: 12px !important;
        border: 1px solid {p['border']} !important;
        box-shadow: {p['card_shadow']} !important;
        object-fit: contain !important;
        /* SIN filter: blur ni filter: brightness — preserva nitidez */
    }}

    /* ── INPUTS DE STREAMLIT ───────────────────────────────────────── */
    .stRadio > label,
    .stSlider > label,
    .stSelectbox > label,
    .stCheckbox > label,
    [data-testid="stSelectSlider"] > label {{
        color: {p['text_primary']} !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {p['bg_card']} !important;
        border-color: {p['border']} !important;
        color: {p['text_primary']} !important;
        border-radius: 10px !important;
    }}

    [data-testid="stFileUploader"] {{
        background-color: {p['bg_card']} !important;
        border: 2px dashed {p['cyan']}45 !important;
        border-radius: 14px !important;
        padding: 16px !important;
        transition: border-color 0.25s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: {p['cyan']}80 !important;
    }}

    /* Radio horizontal — selector Imagen / Cámara */
    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
        font-weight: 600;
        font-size: 0.9rem;
    }}

    /* ── MÉTRICAS ──────────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: {p['bg_elevated']};
        border: 1px solid {p['border']};
        border-radius: 12px;
        padding: 14px 16px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {p['text_sec']} !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    [data-testid="stMetricValue"] {{
        color: {p['text_primary']} !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }}

    /* ── DATAFRAME / TABLA ─────────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid {p['border']} !important;
    }}

    /* ── RESPONSIVE ────────────────────────────────────────────────── */
    @media (max-width: 768px) {{
        .hero-banner {{
            padding: 22px 18px;
            border-radius: 14px;
        }}

        .hero-title {{
            font-size: 26px;
        }}

        .camera-info-grid {{
            grid-template-columns: 1fr 1fr;
        }}

        .card-title-row {{
            flex-direction: column;
            align-items: flex-start;
        }}

        .hero-pills {{
            gap: 8px;
        }}

        .status-pill {{
            font-size: 0.74rem;
            padding: 5px 10px;
        }}
    }}

    @media (max-width: 480px) {{
        .camera-info-grid {{
            grid-template-columns: 1fr;
        }}

        .hero-subtitle {{
            font-size: 0.88rem;
        }}
    }}
    </style>
    """


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENTES HTML REUTILIZABLES
# ──────────────────────────────────────────────────────────────────────────────

def render_header(num_modelos: int = 3, tema: str = "dark", hardware_label: str = "CPU"):
    """
    Renderiza el encabezado principal de la aplicación.
    Sin emojis. Utiliza status pills con puntos CSS de color.
    """
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1 class="hero-title">
                Aulas <span>Atentas</span>
            </h1>
            <p class="hero-subtitle">
                Sistema inteligente de detección de fatiga, posturas y atención estudiantil
            </p>
            <div class="hero-pills">
                <div class="status-pill status-pill-active">
                    <div class="status-dot status-dot-green"></div>
                    Sistema operativo
                </div>
                <div class="status-pill status-pill-info">
                    {num_modelos} modelos cargados
                </div>
                <div class="status-pill">
                    Procesamiento: {hardware_label}
                </div>
                <div class="status-pill">
                    YOLOv8
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_empty_detections():
    """Estado vacío cuando no hay detecciones, sin emojis."""
    st.markdown(
        """
        <div class="empty-state-card">
            <div class="empty-state-title">Sin detecciones</div>
            No se encontraron detecciones con el nivel de confianza seleccionado.<br>
            <span style="font-size:0.82rem;opacity:0.7;">
                Ajusta el umbral de confianza mínima en el panel lateral.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_warning_card(texto: str):
    """Tarjeta de advertencia sin emojis."""
    st.markdown(
        f'<div class="warning-card">{texto}</div>',
        unsafe_allow_html=True
    )


def render_info_card(texto: str):
    """Tarjeta de información sin emojis."""
    st.markdown(
        f'<div class="info-card">{texto}</div>',
        unsafe_allow_html=True
    )


def render_no_image_state():
    """Estado sin imagen cargada, sin emojis."""
    st.markdown(
        """
        <div class="dropzone-card">
            <div class="dropzone-title">Cargar imagen para analizar</div>
            <div class="dropzone-subtitle">
                Arrastra una imagen aquí o selecciónala desde tu dispositivo.<br>
                Formatos permitidos: JPG, JPEG y PNG.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
