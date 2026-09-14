"""
Aulas Atentas — Dashboard de monitoreo académico con IA.
Detecta fatiga, posturas y atención estudiantil mediante modelos YOLOv8.
"""

from pathlib import Path
import threading
import time

import av
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import torch
from PIL import Image
from ultralytics import YOLO
from streamlit_webrtc import (
    VideoProcessorBase,
    WebRtcMode,
    webrtc_streamer
)

from styles import (
    get_css,
    render_header,
    render_empty_detections,
    render_warning_card,
    render_info_card,
    render_no_image_state,
)

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Aulas Atentas",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
CARPETA_MODELOS = BASE_DIR / "models"

RUTAS_MODELOS = {
    "Fatiga": (
        CARPETA_MODELOS / "fatigue_yolov8n_best.pt"
    ),
    "Posturas y actividades": (
        CARPETA_MODELOS / "class_monitoring_yolov8n_best.pt"
    ),
    "Atención estudiantil": (
        CARPETA_MODELOS / "student_attention_yolov8n_best.pt"
    ),
}

# ============================================================
# TRADUCCIÓN DE CLASES AL ESPAÑOL
# ============================================================

TRADUCCIONES = {
    "Fatiga": {
        "Closed Eye": "Ojo cerrado",
        "No Yawn":    "Sin bostezo",
        "Open Eye":   "Ojo abierto",
        "Yawn":       "Bostezo",
    },
    "Posturas y actividades": {
        "Using_phone":  "Usando el teléfono",
        "bend":         "Agachado",
        "bow_head":     "Cabeza inclinada",
        "hand-raising": "Mano levantada",
        "reading":      "Leyendo",
        "sleep":        "Dormido",
        "turn_head":    "Girando la cabeza",
        "upright":      "Erguido",
        "writing":      "Escribiendo",
    },
    "Atención estudiantil": {
        "attentive":             "Atento",
        "crossing legs":         "Piernas cruzadas",
        "daydreaming":           "Soñando despierto",
        "distracted":            "Distraído",
        "hand-raising":          "Mano levantada",
        "looking at the screen": "Mirando la pantalla",
        "phone Use":             "Uso del teléfono",
        "reading":               "Leyendo",
        "sleepy":                "Somnoliento",
        "teaching":              "Enseñando",
        "using a phone":         "Usando el teléfono",
        "writing":               "Escribiendo",
    },
}

# Colores de acento por modelo — se usan como clase CSS
COLOR_MODELO = {
    "Fatiga":                 "fatigue",
    "Posturas y actividades": "postures",
    "Atención estudiantil":   "attention",
}

# Color del punto de estado por modelo
DOT_MODELO = {
    "Fatiga":                 "status-dot-violet",
    "Posturas y actividades": "status-dot-cyan",
    "Atención estudiantil":   "status-dot-green",
}


def obtener_nombres_espanol(nombre_modelo: str, modelo) -> dict:
    """Devuelve un mapa índice → nombre en español para las clases del modelo."""
    nombres_originales = modelo.names
    elementos = (
        nombres_originales.items()
        if isinstance(nombres_originales, dict)
        else enumerate(nombres_originales)
    )
    return {
        int(idx): TRADUCCIONES.get(nombre_modelo, {}).get(nombre, nombre)
        for idx, nombre in elementos
    }


# ============================================================
# CARGAR MODELOS YOLO — cacheados para no recargar en cada interacción
# ============================================================

@st.cache_resource
def cargar_modelos() -> dict:
    modelos = {}
    for nombre, ruta in RUTAS_MODELOS.items():
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo en: {ruta}"
            )
        modelos[nombre] = YOLO(str(ruta))
    return modelos


try:
    modelos = cargar_modelos()
    num_modelos_cargados = len(modelos)
except Exception as error:
    st.error(f"Error al cargar los modelos de visión artificial: {error}")
    st.stop()


# ============================================================
# PREPROCESAMIENTO — SOLO PARA INFERENCIA, NUNCA PARA MOSTRAR
# ============================================================

def preprocesar_frame_bgr(frame_bgr: np.ndarray) -> np.ndarray:
    """
    Aplica mejora de contraste CLAHE en el espacio LAB.

    IMPORTANTE: Esta función SOLO debe llamarse sobre una COPIA del frame.
    Nunca debe modificar el frame que se muestra al usuario.
    El frame original sin procesar es siempre el que se visualiza.
    """
    imagen_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    canal_l, canal_a, canal_b = cv2.split(imagen_lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    canal_l = clahe.apply(canal_l)
    imagen_lab = cv2.merge((canal_l, canal_a, canal_b))
    return cv2.cvtColor(imagen_lab, cv2.COLOR_LAB2BGR)


def preprocesar_imagen(imagen_pil: Image.Image) -> np.ndarray:
    """Convierte PIL RGB → BGR y aplica CLAHE. Solo para inferencia."""
    imagen_rgb = np.array(imagen_pil)
    imagen_bgr = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2BGR)
    return preprocesar_frame_bgr(imagen_bgr)


# ============================================================
# SIDEBAR — PANEL DE CONTROL
# ============================================================

st.sidebar.markdown("## Panel de Control")

# ── Tema visual ─────────────────────────────────────────────
tema = st.sidebar.radio(
    "Modo Visual",
    ["Modo oscuro", "Modo claro"],
    index=0,
    help="Cambia entre tema oscuro y tema claro.",
)
theme_code = "dark" if "oscuro" in tema else "light"

# Inyectar CSS del tema seleccionado
st.markdown(get_css(theme_code), unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### Modo de Análisis")

modo_analisis = st.sidebar.radio(
    "Selecciona el modo:",
    ["Aula", "Primer plano", "Todos los modelos"],
    index=0,
)

# Modelos activos según el modo
if modo_analisis == "Aula":
    st.sidebar.info(
        "**Aula:** Detecta posturas, actividades y nivel de atención.\n\n"
        "Modelos: Posturas y actividades, Atención estudiantil."
    )
    modelos_activos = {
        "Posturas y actividades": modelos["Posturas y actividades"],
        "Atención estudiantil":   modelos["Atención estudiantil"],
    }

elif modo_analisis == "Primer plano":
    st.sidebar.info(
        "**Primer plano:** Analiza signos visuales de fatiga en el rostro.\n\n"
        "Modelo: Fatiga."
    )
    modelos_activos = {"Fatiga": modelos["Fatiga"]}

else:
    st.sidebar.info(
        "**Todos los modelos:** Ejecuta los tres modelos para una demostración completa."
    )
    st.sidebar.warning(
        "Este modo puede producir detecciones superpuestas y requerir más procesamiento."
    )
    modelos_activos = modelos

num_modelos_activos = len(modelos_activos)

st.sidebar.markdown("---")
st.sidebar.markdown("### Parámetros de Inferencia")

confianza = st.sidebar.slider(
    "Confianza mínima",
    min_value=0.10,
    max_value=0.90,
    value=0.35,
    step=0.05,
    help="Filtra detecciones con confianza por debajo del umbral.",
)

tamanio_inferencia = st.sidebar.select_slider(
    "Tamaño de inferencia (px)",
    options=[320, 512, 640],
    value=320,
    help="320 px es ideal en CPU. Mayor tamaño aumenta la precisión pero reduce la velocidad.",
)

# ── Frame skip ──────────────────────────────────────────────
# Controla cada cuántos frames ejecuta YOLO.
# Con más modelos activos se sugiere un skip mayor.
skip_sugerido = 5 if num_modelos_activos <= 1 else (8 if num_modelos_activos >= 3 else 5)

frame_skip = st.sidebar.select_slider(
    "Procesar un frame cada",
    options=[1, 3, 5, 8],
    value=skip_sugerido,
    help=(
        "Mayor valor → cámara más fluida, inferencia menos frecuente. "
        f"Sugerido para {num_modelos_activos} modelo(s): {skip_sugerido}."
    ),
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Configuración de Cámara")

# ── Sensor de cámara ────────────────────────────────────────
camara_tipo = st.sidebar.selectbox(
    "Sensor de cámara",
    ["Frontal (Selfie)", "Trasera (Principal)", "Automática"],
    index=0,
    help=(
        "Frontal: ideal para laptops y selfies. "
        "Trasera: principal en dispositivos móviles. "
        "Automática: el navegador elige."
    ),
)

if "Frontal" in camara_tipo:
    facing_mode = "user"
    facing_mode_constraint = {"ideal": "user"}
elif "Trasera" in camara_tipo:
    facing_mode = "environment"
    facing_mode_constraint = {"ideal": "environment"}
else:
    facing_mode = "auto"
    facing_mode_constraint = None

rotacion_video = st.sidebar.selectbox(
    "Rotación de video",
    ["Sin rotación", "90° Derecha", "180°", "90° Izquierda (270°)"],
    index=0,
    help="Corrige la orientación si la cámara trasera aparece de lado.",
)

# ── Resolución de cámara ────────────────────────────────────
res_camara_str = st.sidebar.selectbox(
    "Resolución de cámara",
    ["Automática", "HD (1280×720)", "Full HD (1920×1080)", "Estándar (640×480)"],
    index=1,  # HD como predeterminado
    help=(
        "Resolución solicitada al navegador. Si la cámara no la soporta, "
        "el navegador negocia automáticamente (mínimo 640×480)."
    ),
)

if "1920" in res_camara_str:
    cam_width, cam_height = 1920, 1080
elif "1280" in res_camara_str:
    cam_width, cam_height = 1280, 720
elif "640" in res_camara_str:
    cam_width, cam_height = 640, 480
else:
    cam_width, cam_height = None, None  # Automática

# ── Preprocesamiento CLAHE ──────────────────────────────────
activar_preprocesamiento = st.sidebar.checkbox(
    "Activar mejora CLAHE para modelo",
    value=False,
    help=(
        "Aplica mejora de contraste CLAHE ÚNICAMENTE sobre la copia interna "
        "que recibe YOLO. El video que visualizas nunca es modificado."
    ),
)

# ── Hardware ────────────────────────────────────────────────
gpu_disponible  = torch.cuda.is_available()
device_arg      = "0" if gpu_disponible else "cpu"
hardware_label  = "GPU (CUDA)" if gpu_disponible else "CPU"

st.sidebar.markdown("---")
st.sidebar.markdown("### Estado del Sistema")

# Bloque de estado sin emojis
clahe_estado = "Activo (solo para YOLO)" if activar_preprocesamiento else "Desactivado"
res_display   = f"{cam_width}×{cam_height}" if cam_width else "Automática"

st.sidebar.markdown(
    f"""
    <div class="sidebar-status-block">
        <div class="sidebar-status-row">
            <span>Modelos activos</span>
            <span class="sidebar-status-value">{num_modelos_activos} / 3</span>
        </div>
        <div class="sidebar-status-row">
            <span>Hardware</span>
            <span class="sidebar-status-value">{hardware_label}</span>
        </div>
        <div class="sidebar-status-row">
            <span>Frame skip</span>
            <span class="sidebar-status-value">Cada {frame_skip} frames</span>
        </div>
        <div class="sidebar-status-row">
            <span>Filtro CLAHE</span>
            <span class="sidebar-status-value">{clahe_estado}</span>
        </div>
        <div class="sidebar-status-row">
            <span>Resolución</span>
            <span class="sidebar-status-value">{res_display}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================

render_header(
    num_modelos=num_modelos_cargados,
    tema=theme_code,
    hardware_label=hardware_label,
)

# ── Selector de modo de entrada ─────────────────────────────
tipo_entrada = st.radio(
    "Tipo de entrada:",
    ["Cargar imagen", "Cámara en vivo"],
    horizontal=True,
)


# ============================================================
# MODO: CARGAR IMAGEN
# ============================================================

if tipo_entrada == "Cargar imagen":

    archivo = st.file_uploader(
        "Arrastra una imagen aquí o selecciónala desde tu dispositivo",
        type=["jpg", "jpeg", "png"],
        key="cargador_imagen",
        help="Formatos permitidos: JPG, JPEG y PNG.",
    )

    if archivo is None:
        render_no_image_state()

    else:
        # ── Frame original — para mostrar al usuario ─────────────────
        imagen_original = Image.open(archivo).convert("RGB")
        imagen_bgr_original = cv2.cvtColor(
            np.array(imagen_original), cv2.COLOR_RGB2BGR
        )

        # ── Frame de inferencia — copia separada, solo para YOLO ─────
        if activar_preprocesamiento:
            imagen_para_modelo = preprocesar_imagen(imagen_original)
        else:
            imagen_para_modelo = imagen_bgr_original.copy()

        # Previsualización
        col_orig, col_prep = st.columns(2)

        with col_orig:
            st.markdown(
                '<div class="img-card"><div class="img-card-title">Imagen original</div>',
                unsafe_allow_html=True,
            )
            st.image(imagen_original, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_prep:
            st.markdown(
                '<div class="img-card"><div class="img-card-title">Imagen para inferencia</div>',
                unsafe_allow_html=True,
            )
            st.image(
                cv2.cvtColor(imagen_para_modelo, cv2.COLOR_BGR2RGB),
                use_container_width=True,
            )
            if activar_preprocesamiento:
                st.caption("Mejora de contraste CLAHE aplicada antes de la inferencia.")
            else:
                st.caption("Preprocesamiento desactivado — imagen original sin modificar.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Resultados por modelo")

        # ── Resultado de cada modelo en su propia tarjeta ─────────────
        for nombre_modelo, modelo in modelos_activos.items():

            estilo_card = COLOR_MODELO.get(nombre_modelo, "postures")
            dot_class   = DOT_MODELO.get(nombre_modelo, "status-dot-cyan")

            with st.container():
                st.markdown(
                    f"""
                    <div class="custom-card model-card-{estilo_card}">
                        <div class="card-title-row">
                            <div class="card-title-text">{nombre_modelo}</div>
                            <div class="status-pill status-pill-active">
                                <div class="status-dot {dot_class}"></div>
                                Ejecutado correctamente
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                t_inicio = time.time()
                try:
                    # Inferencia sobre la copia preprocesada (NUNCA sobre el original)
                    resultado = modelo.predict(
                        source=imagen_para_modelo,
                        device=device_arg,
                        imgsz=tamanio_inferencia,
                        conf=confianza,
                        verbose=False,
                    )[0]
                except Exception as ex_inf:
                    st.error(f"Error en el modelo {nombre_modelo}: {ex_inf}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    continue

                t_fin     = time.time()
                tiempo_ms = round((t_fin - t_inicio) * 1000, 1)

                # Traducir nombres al español
                nombres_es       = obtener_nombres_espanol(nombre_modelo, modelo)
                resultado.names  = nombres_es

                # Dibujar cajas sobre el frame ORIGINAL nítido
                imagen_anotada = resultado.plot(img=imagen_bgr_original.copy())
                imagen_anotada_rgb = cv2.cvtColor(imagen_anotada, cv2.COLOR_BGR2RGB)

                num_detecciones = (
                    0 if resultado.boxes is None else len(resultado.boxes)
                )

                col_metrics, col_visual = st.columns([1, 2])

                with col_metrics:
                    st.metric("Tiempo de inferencia", f"{tiempo_ms} ms")
                    st.metric("Detecciones", f"{num_detecciones}")

                with col_visual:
                    st.image(
                        imagen_anotada_rgb,
                        caption=f"Resultado — {nombre_modelo}",
                        use_container_width=True,
                    )

                # Tabla de resultados
                if num_detecciones == 0:
                    render_empty_detections()
                else:
                    filas = []
                    clases     = resultado.boxes.cls.cpu().tolist()
                    confianzas = resultado.boxes.conf.cpu().tolist()

                    for clase, conf_val in zip(clases, confianzas):
                        clase_idx    = int(clase)
                        nombre_clase = nombres_es.get(clase_idx, f"Clase {clase_idx}")
                        conf_pct     = round(float(conf_val) * 100, 1)
                        conf_dec     = round(float(conf_val), 3)

                        if conf_dec >= 0.75:
                            nivel_str = "Alta (> 75%)"
                        elif conf_dec >= 0.50:
                            nivel_str = "Media (50 – 75%)"
                        else:
                            nivel_str = "Baja (< 50%)"

                        filas.append({
                            "Clase detectada":   nombre_clase,
                            "Confianza":         conf_dec,
                            "Nivel de confianza": nivel_str,
                            "Indicador":         conf_dec,
                        })

                    df_res = pd.DataFrame(filas)

                    # Pills de clases sin emojis
                    clases_unicas = df_res["Clase detectada"].unique()
                    pills_html = "".join(
                        f'<span class="class-pill">{c}</span>'
                        for c in clases_unicas
                    )
                    st.markdown(
                        f"<div style='margin-bottom:12px;'>"
                        f"<span style='font-size:0.8rem;font-weight:700;"
                        f"text-transform:uppercase;letter-spacing:0.06em;"
                        f"opacity:0.6;'>Etiquetas detectadas</span><br/>"
                        f"{pills_html}</div>",
                        unsafe_allow_html=True,
                    )

                    st.dataframe(
                        df_res,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Confianza": st.column_config.NumberColumn(
                                "Confianza",
                                format="%.3f",
                            ),
                            "Indicador": st.column_config.ProgressColumn(
                                "Nivel visual",
                                min_value=0.0,
                                max_value=1.0,
                                format="%.0%",
                            ),
                        },
                    )

                st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODO: CÁMARA EN VIVO — Separación frame original / inferencia
# ============================================================

else:

    # Aviso para modo "Todos los modelos"
    if modo_analisis == "Todos los modelos":
        render_warning_card(
            "En modo Todos los modelos se recomienda aumentar el frame skip a "
            "<strong>8</strong> y usar tamaño de inferencia de "
            "<strong>320 px</strong> para mantener la cámara fluida."
        )

    # Aviso cámara trasera en laptop
    if "Trasera" in camara_tipo:
        render_info_card(
            "Cámara trasera seleccionada. En laptops normalmente solo existe la cámara frontal; "
            "si el navegador no encuentra la cámara trasera, usará la disponible automáticamente."
        )

    # ── Cabecera de la tarjeta de cámara ────────────────────────────
    modelos_activos_nombres = ", ".join(modelos_activos.keys())

    st.markdown(
        f"""
        <div class="custom-card">
            <div class="card-title-row">
                <div class="card-title-text">Monitoreo en vivo</div>
                <div class="status-pill status-pill-active">
                    <div class="status-dot status-dot-green"></div>
                    Cámara activa
                </div>
            </div>
            <div class="camera-info-grid">
                <div class="camera-info-item">
                    <span class="camera-info-label">Modo</span>
                    <span class="camera-info-value">{modo_analisis}</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Sensor</span>
                    <span class="camera-info-value">{camara_tipo}</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Resolución solicitada</span>
                    <span class="camera-info-value">{res_display}</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Hardware</span>
                    <span class="camera-info-value">{hardware_label}</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Frame skip</span>
                    <span class="camera-info-value">Cada {frame_skip} frames</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Modelos activos</span>
                    <span class="camera-info-value">{modelos_activos_nombres}</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Inferencia YOLO</span>
                    <span class="camera-info-value">{tamanio_inferencia} px</span>
                </div>
                <div class="camera-info-item">
                    <span class="camera-info-label">Filtro CLAHE</span>
                    <span class="camera-info-value">{clahe_estado}</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # PROCESADOR WEBRTC — Separación explícita de frames
    # ============================================================

    class ProcesadorCamaraAsincronoCloud(VideoProcessorBase):
        """
        Procesador WebRTC con separación clara entre frame original y frame de inferencia.

        Arquitectura:
        ──────────────────────────────────────────────────────────────────────
        recv()
            → Captura frame_original (calidad nativa, NUNCA se modifica)
            → Aplica frame skip: encola frame_inferencia solo 1 de cada N
            → frame_inferencia = copia del original + CLAHE opcional
            → Obtiene la última detección del worker
            → Dibuja cajas sobre frame_original (nunca sobre el preprocesado)
            → Devuelve frame_anotado en bgr24

        _worker_inferencia()
            → Consume frame_inferencia de la cola (capacidad 1)
            → Ejecuta YOLO sobre la copia preprocesada
            → Guarda resultados en self.latest_results
            → No toca frame_original en ningún momento
        ──────────────────────────────────────────────────────────────────────
        """

        def __init__(
            self,
            modelos: dict,
            confianza: float,
            device: str = "cpu",
            imgsz: int = 320,
            preprocesar: bool = False,
            rotacion: str = "Sin rotación",
            frame_skip: int = 5,
        ):
            self.modelos      = modelos
            self.confianza    = confianza
            self.device       = device
            self.imgsz        = imgsz
            self.preprocesar  = preprocesar
            self.rotacion     = rotacion
            self.frame_skip   = max(1, frame_skip)

            # Estado compartido protegido con lock
            self.lock    = threading.Lock()
            self.running = True

            # Cola de un frame para el worker (capacidad = 1)
            self.latest_frame_for_inference = None

            # Resultados de la última inferencia completada
            self.latest_results = []

            # Métricas
            self.last_inference_ms    = 0.0
            self.last_detection_count = 0
            self.frame_counter        = 0

            # Hilo de inferencia desacoplado
            self.thread = threading.Thread(
                target=self._worker_inferencia,
                daemon=True,
            )
            self.thread.start()

        def _worker_inferencia(self):
            """
            Hilo secundario de inferencia.
            Consume la copia preprocesada del frame y ejecuta YOLO.
            Descarta frames acumulados para evitar retraso progresivo.
            """
            while self.running:
                frame_para_inferencia = None

                with self.lock:
                    if self.latest_frame_for_inference is not None:
                        frame_para_inferencia           = self.latest_frame_for_inference
                        self.latest_frame_for_inference = None

                if frame_para_inferencia is not None:
                    t_inicio         = time.time()
                    nuevos_resultados = []
                    total_detecciones = 0

                    for nombre_modelo, modelo in self.modelos.items():
                        try:
                            # ── INFERENCIA SOBRE COPIA PREPROCESADA ──────────
                            # YOLO recibe frame_para_inferencia.
                            # Los resultados se escalan automáticamente al tamaño real.
                            res = modelo.predict(
                                source=frame_para_inferencia,
                                device=self.device,
                                imgsz=self.imgsz,
                                conf=self.confianza,
                                verbose=False,
                            )[0]

                            nombres_es = obtener_nombres_espanol(nombre_modelo, modelo)
                            res.names  = nombres_es
                            nuevos_resultados.append(res)

                            if res.boxes is not None:
                                total_detecciones += len(res.boxes)

                        except Exception:
                            pass

                    t_fin = time.time()

                    with self.lock:
                        self.latest_results        = nuevos_resultados
                        self.last_inference_ms     = round((t_fin - t_inicio) * 1000, 1)
                        self.last_detection_count  = total_detecciones
                else:
                    time.sleep(0.01)

        def recv(self, frame):
            """
            Callback principal del stream WebRTC.

            Separación de frames:
            ──────────────────────────────────────────────────────────────
            1. frame_original  → Calidad nativa. El usuario SIEMPRE lo ve.
                                 No recibe ningún preprocesamiento.
            2. frame_inferencia→ Copia independiente. Solo si frame_skip OK.
                                 CLAHE opcional. Solo para YOLO.
            3. frame_anotado   → frame_original + cajas de la última detección.
                                 Es lo que se devuelve al stream WebRTC.
            ──────────────────────────────────────────────────────────────
            """
            # ── 1. FRAME ORIGINAL — Calidad nativa ───────────────────────
            frame_original = frame.to_ndarray(format="bgr24")

            if self.rotacion == "90° Derecha":
                frame_original = cv2.rotate(frame_original, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotacion == "180°":
                frame_original = cv2.rotate(frame_original, cv2.ROTATE_180)
            elif self.rotacion == "90° Izquierda (270°)":
                frame_original = cv2.rotate(frame_original, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # ── 2. FRAME PARA INFERENCIA — Copia con frame skip ──────────
            with self.lock:
                self.frame_counter += 1
                enqueue_frame = (self.frame_counter % self.frame_skip == 0)

            if enqueue_frame:
                frame_inferencia = frame_original.copy()
                # CLAHE solo sobre la copia de inferencia; frame_original intacto
                if self.preprocesar:
                    frame_inferencia = preprocesar_frame_bgr(frame_inferencia)
                with self.lock:
                    self.latest_frame_for_inference = frame_inferencia

            # ── 3. DETECCIONES MÁS RECIENTES ─────────────────────────────
            with self.lock:
                resultados_actuales = list(self.latest_results)

            # ── 4. DEVOLVER FRAME ORIGINAL + CAJAS ───────────────────────
            if not resultados_actuales:
                # Sin detecciones aún: devolver el frame nativo sin conversión extra
                return frame

            frame_anotado = frame_original.copy()
            for res in resultados_actuales:
                try:
                    frame_anotado = res.plot(img=frame_anotado)
                except Exception:
                    pass

            return av.VideoFrame.from_ndarray(frame_anotado, format="bgr24")

    # ── Factory del procesador ────────────────────────────────────────
    def crear_procesador():
        return ProcesadorCamaraAsincronoCloud(
            modelos=modelos_activos,
            confianza=confianza,
            device=device_arg,
            imgsz=tamanio_inferencia,
            preprocesar=activar_preprocesamiento,
            rotacion=rotacion_video,
            frame_skip=frame_skip,
        )

    # ── Construir restricciones WebRTC ───────────────────────────────
    # Usa "ideal" + "min" para negociar la mejor resolución sin fallar.
    video_constraints: dict = {
        "frameRate": {"ideal": 30, "max": 30}
    }

    if cam_width and cam_height:
        video_constraints["width"]  = {"ideal": cam_width,  "min": 640}
        video_constraints["height"] = {"ideal": cam_height, "min": 480}

    if facing_mode_constraint is not None:
        video_constraints["facingMode"] = facing_mode_constraint

    # La clave cambia cuando cambia cualquier parámetro de cámara o inferencia,
    # lo que fuerza al navegador a reiniciar el stream correctamente.
    stream_key = (
        f"cam_{facing_mode}_{res_camara_str}_{frame_skip}"
        f"_{modo_analisis}_{tamanio_inferencia}"
    )

    webrtc_streamer(
        key=stream_key,
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
                {"urls": ["stun:stun2.l.google.com:19302"]},
            ]
        },
        video_processor_factory=crear_procesador,
        media_stream_constraints={
            "video": video_constraints,
            "audio": False,
        },
        async_processing=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)