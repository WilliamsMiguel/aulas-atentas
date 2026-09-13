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

from styles import get_css, render_header, render_empty_detections

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Aulas Atentas - Dashboard",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
CARPETA_MODELOS = BASE_DIR / "models"

RUTAS_MODELOS = {
    "Fatiga": (
        CARPETA_MODELOS /
        "fatigue_yolov8n_best.pt"
    ),

    "Posturas y actividades": (
        CARPETA_MODELOS /
        "class_monitoring_yolov8n_best.pt"
    ),

    "Atención estudiantil": (
        CARPETA_MODELOS /
        "student_attention_yolov8n_best.pt"
    )
}


# ============================================================
# TRADUCCIÓN DE CLASES AL ESPAÑOL
# ============================================================

TRADUCCIONES = {
    "Fatiga": {
        "Closed Eye": "Ojo cerrado",
        "No Yawn": "Sin bostezo",
        "Open Eye": "Ojo abierto",
        "Yawn": "Bostezo"
    },

    "Posturas y actividades": {
        "Using_phone": "Usando el teléfono",
        "bend": "Agachado",
        "bow_head": "Cabeza inclinada",
        "hand-raising": "Mano levantada",
        "reading": "Leyendo",
        "sleep": "Dormido",
        "turn_head": "Girando la cabeza",
        "upright": "Erguido",
        "writing": "Escribiendo"
    },

    "Atención estudiantil": {
        "attentive": "Atento",
        "crossing legs": "Piernas cruzadas",
        "daydreaming": "Soñando despierto",
        "distracted": "Distraído",
        "hand-raising": "Mano levantada",
        "looking at the screen": "Mirando la pantalla",
        "phone Use": "Uso del teléfono",
        "reading": "Leyendo",
        "sleepy": "Somnoliento",
        "teaching": "Enseñando",
        "using a phone": "Usando el teléfono",
        "writing": "Escribiendo"
    }
}


def obtener_nombres_espanol(nombre_modelo, modelo):

    nombres_originales = modelo.names

    if isinstance(nombres_originales, dict):
        elementos = nombres_originales.items()
    else:
        elementos = enumerate(nombres_originales)

    nombres_espanol = {}

    for indice, nombre in elementos:

        nombres_espanol[int(indice)] = TRADUCCIONES.get(
            nombre_modelo,
            {}
        ).get(nombre, nombre)

    return nombres_espanol


# ============================================================
# CARGAR MODELOS YOLO
# ============================================================

@st.cache_resource
def cargar_modelos():

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
    st.error(
        f"Error técnico al cargar los modelos de visión artificial: {error}"
    )
    st.stop()


# ============================================================
# MEJORA DE CONTRASTE OPTIMIZADA (SIN DESENFOQUE GAUSSIANO)
# ============================================================

def preprocesar_frame_bgr(frame_bgr):

    imagen_lab = cv2.cvtColor(
        frame_bgr,
        cv2.COLOR_BGR2LAB
    )

    canal_l, canal_a, canal_b = cv2.split(
        imagen_lab
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    canal_l = clahe.apply(canal_l)

    imagen_lab = cv2.merge(
        (canal_l, canal_a, canal_b)
    )

    return cv2.cvtColor(
        imagen_lab,
        cv2.COLOR_LAB2BGR
    )


def preprocesar_imagen(imagen_pil):

    imagen_rgb = np.array(imagen_pil)

    imagen_bgr = cv2.cvtColor(
        imagen_rgb,
        cv2.COLOR_RGB2BGR
    )

    return preprocesar_frame_bgr(imagen_bgr)


# ============================================================
# BARRA LATERAL Y PANEL DE CONFIGURACIÓN
# ============================================================

st.sidebar.markdown("## ⚙️ Panel de Control")

# Selector de Tema Visual (Oscuro / Claro)
tema = st.sidebar.radio(
    "🎨 Modo Visual",
    ["Oscuro", "Claro"],
    index=0,
    help="Cambia entre modo oscuro y claro."
)
theme_code = "dark" if tema == "Oscuro" else "light"

# Inyectar CSS personalizado adaptativo
st.markdown(get_css(theme_code), unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Modo de Análisis")

modo_analisis = st.sidebar.radio(
    "Selecciona el modo:",
    [
        "Aula",
        "Primer plano",
        "Todos los modelos"
    ],
    index=0
)

# Descripciones claras de los modos
if modo_analisis == "Aula":

    st.sidebar.info(
        "**Aula:** Detecta posturas, actividades y nivel de atención en escenas completas.\n\n"
        "**Modelos utilizados:**\n"
        "• Posturas y actividades\n"
        "• Atención estudiantil"
    )

    modelos_activos = {
        "Posturas y actividades":
            modelos["Posturas y actividades"],

        "Atención estudiantil":
            modelos["Atención estudiantil"]
    }

elif modo_analisis == "Primer plano":

    st.sidebar.info(
        "**Primer plano:** Analiza el rostro para identificar signos visuales de fatiga.\n\n"
        "**Modelo utilizado:**\n"
        "• Fatiga"
    )

    modelos_activos = {
        "Fatiga": modelos["Fatiga"]
    }

else:

    st.sidebar.info(
        "**Todos los modelos:** Ejecuta los tres modelos simultáneamente para una demostración completa."
    )

    st.sidebar.warning(
        "⚠️ Este modo puede generar detecciones superpuestas y consumir más recursos."
    )

    modelos_activos = modelos


st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parámetros de Inferencia")

confianza = st.sidebar.slider(
    "Confianza mínima",
    min_value=0.10,
    max_value=0.90,
    value=0.35,
    step=0.05,
    help="Filtra detecciones con nivel de confianza inferior al umbral."
)

tamanio_inferencia = st.sidebar.select_slider(
    "Tamaño de imagen (px)",
    options=[512, 640],
    value=640,
    help="Un tamaño menor acelera el procesamiento."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Configuración de Cámara Móvil")

camara_tipo = st.sidebar.selectbox(
    "Sensor de Cámara",
    ["Frontal (Selfie)", "Trasera (Principal)"],
    index=0,
    help="Define el sensor utilizado por el navegador en celulares."
)
facing_mode = "user" if "Frontal" in camara_tipo else "environment"

rotacion_video = st.sidebar.selectbox(
    "Rotación de Video",
    ["Sin rotación", "90° Derecha", "180°", "90° Izquierda (270°)"],
    index=0,
    help="Corrige la orientación si la cámara trasera se transmite de lado."
)

res_camara_str = st.sidebar.selectbox(
    "Resolución de Cámara Web",
    [
        "HD (1280x720)",
        "Full HD (1920x1080)",
        "Estándar (640x480)"
    ],
    index=0,
    help="Resolución de captura enviada por el navegador."
)

if "1920x1080" in res_camara_str:
    cam_width, cam_height = 1920, 1080
elif "640x480" in res_camara_str:
    cam_width, cam_height = 640, 480
else:
    cam_width, cam_height = 1280, 720

# Selección de CPU/GPU
gpu_disponible = torch.cuda.is_available()
opciones_dispositivo = ["CPU"]
if gpu_disponible:
    opciones_dispositivo.append("GPU (CUDA)")

dispositivo_sel = st.sidebar.selectbox(
    "Dispositivo de Inferencia",
    opciones_dispositivo,
    index=0,
    help="Aceleración hardware disponible."
)

device_arg = "0" if dispositivo_sel.startswith("GPU") and gpu_disponible else "cpu"

activar_preprocesamiento = st.sidebar.checkbox(
    "Activar Mejora CLAHE",
    value=False,
    help="Aplica mejora de contraste CLAHE a la entrada del modelo."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estado del Sistema")
st.sidebar.markdown(f"• **Modelos activos:** {len(modelos_activos)} / 3")
st.sidebar.markdown(f"• **Hardware:** `{dispositivo_sel}`")
if activar_preprocesamiento:
    st.sidebar.markdown("• **Filtro modelo:** CLAHE Activo")
else:
    st.sidebar.markdown("• **Filtro modelo:** Desactivado (Nítido)")


# ============================================================
# ENCABEZADO PRINCIPAL (HERO BANNER)
# ============================================================

render_header(num_modelos=num_modelos_cargados, tema=theme_code)

tipo_entrada = st.radio(
    "Selecciona el tipo de entrada:",
    [
        "🖼️ Cargar Imagen",
        "📹 Cámara en Vivo"
    ],
    horizontal=True
)


# ============================================================
# MODO: CARGAR IMAGEN
# ============================================================

if tipo_entrada == "🖼️ Cargar Imagen":

    archivo = st.file_uploader(
        "Arrastra una imagen o selecciónala desde tu equipo",
        type=["jpg", "jpeg", "png"],
        key="cargador_imagen",
        help="Formatos permitidos: JPG, JPEG y PNG"
    )

    if archivo is None:

        st.markdown(
            """
            <div class="empty-state-card">
                📥 <b>Arrastra una imagen o selecciónala desde tu equipo.</b><br/>
                <span style="font-size: 0.88rem; opacity: 0.8;">Formatos permitidos: JPG, JPEG y PNG.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        imagen_original = Image.open(archivo).convert("RGB")

        imagen_bgr_original = cv2.cvtColor(
            np.array(imagen_original),
            cv2.COLOR_RGB2BGR
        )

        if activar_preprocesamiento:
            imagen_para_modelo = preprocesar_imagen(imagen_original)
        else:
            imagen_para_modelo = imagen_bgr_original

        # Previsualización de imágenes
        col_orig, col_prep = st.columns(2)

        with col_orig:
            st.markdown(
                """
                <div class="img-card">
                    <div class="img-card-title">🖼️ Imagen original</div>
                """,
                unsafe_allow_html=True
            )
            st.image(imagen_original, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_prep:
            st.markdown(
                """
                <div class="img-card">
                    <div class="img-card-title">⚡ Imagen para inferencia</div>
                """,
                unsafe_allow_html=True
            )
            st.image(
                cv2.cvtColor(imagen_para_modelo, cv2.COLOR_BGR2RGB),
                use_container_width=True
            )
            if activar_preprocesamiento:
                st.caption(
                    "Mejora de contraste CLAHE aplicada antes de la inferencia."
                )
            else:
                st.caption("Preprocesamiento desactivado (Imagen original).")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔍 Resultados por Modelo")

        colores_modelos = {
            "Fatiga": "fatigue",
            "Posturas y actividades": "postures",
            "Atención estudiantil": "attention"
        }

        iconos_modelos = {
            "Fatiga": "💤",
            "Posturas y actividades": "🧘",
            "Atención estudiantil": "📚"
        }

        # Procesar cada modelo activo por separado en su tarjeta individual
        for nombre_modelo, modelo in modelos_activos.items():

            estilo_card = colores_modelos.get(nombre_modelo, "postures")
            icono = iconos_modelos.get(nombre_modelo, "🎯")

            with st.container():
                st.markdown(
                    f"""
                    <div class="custom-card model-card-{estilo_card}">
                        <div class="card-title-row">
                            <div class="card-title-text">
                                {icono} {nombre_modelo}
                            </div>
                            <div class="status-pill status-pill-active">
                                <span>Ejecutado correctamente</span>
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                t_inicio = time.time()

                try:
                    resultado = modelo.predict(
                        source=imagen_para_modelo,
                        device=device_arg,
                        imgsz=tamanio_inferencia,
                        conf=confianza,
                        verbose=False
                    )[0]
                except Exception as ex_inf:
                    st.error(f"Error al procesar con el modelo {nombre_modelo}: {ex_inf}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    continue

                t_fin = time.time()
                tiempo_ms = round((t_fin - t_inicio) * 1000, 1)

                nombres_es = obtener_nombres_espanol(nombre_modelo, modelo)
                resultado.names = nombres_es

                # Dibujar siempre las cajas sobre la imagen ORIGINAL NÍTIDA
                imagen_anotada = resultado.plot(img=imagen_bgr_original.copy())
                imagen_anotada_rgb = cv2.cvtColor(
                    imagen_anotada,
                    cv2.COLOR_BGR2RGB
                )

                num_detecciones = (
                    0 if resultado.boxes is None
                    else len(resultado.boxes)
                )

                col_metrics, col_visual = st.columns([1, 2])

                with col_metrics:
                    st.metric("Tiempo de inferencia", f"{tiempo_ms} ms")
                    st.metric("Detecciones encontradas", f"{num_detecciones}")

                with col_visual:
                    st.image(
                        imagen_anotada_rgb,
                        caption=f"Resultado: {nombre_modelo}",
                        use_container_width=True
                    )

                # Tabla de resultados
                if num_detecciones == 0:
                    render_empty_detections()
                else:
                    filas = []
                    clases = resultado.boxes.cls.cpu().tolist()
                    confianzas = resultado.boxes.conf.cpu().tolist()

                    for clase, conf_val in zip(clases, confianzas):

                        clase_idx = int(clase)
                        nombre_clase = nombres_es.get(
                            clase_idx,
                            f"Clase {clase_idx}"
                        )
                        conf_rounded = round(float(conf_val), 3)

                        if conf_rounded >= 0.75:
                            nivel_str = "Alta (>0.75)"
                            estado_tag = "🟢 Alta"
                        elif conf_rounded >= 0.50:
                            nivel_str = "Media (0.50 - 0.75)"
                            estado_tag = "🟡 Media"
                        else:
                            nivel_str = "Baja (<0.50)"
                            estado_tag = "🔴 Baja"

                        filas.append({
                            "Clase detectada": nombre_clase,
                            "Confianza": conf_rounded,
                            "Nivel de Confianza": nivel_str,
                            "Nivel visual": conf_rounded,
                            "Estado": estado_tag
                        })

                    df_res = pd.DataFrame(filas)

                    # Leyenda de clases detectadas
                    clases_unicas = df_res["Clase detectada"].unique()
                    pills_html = "".join(
                        [f'<span class="class-pill">🏷️ {c}</span>' for c in clases_unicas]
                    )

                    st.markdown(
                        f"<div style='margin-bottom:12px;'><b>Etiquetas detectadas:</b> {pills_html}</div>",
                        unsafe_allow_html=True
                    )

                    st.dataframe(
                        df_res,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Confianza": st.column_config.NumberColumn(
                                "Confianza",
                                format="%.3f"
                            ),
                            "Nivel visual": st.column_config.ProgressColumn(
                                "Indicador Visual",
                                min_value=0.0,
                                max_value=1.0,
                                format="%.3f"
                            )
                        }
                    )

                st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODO: CÁMARA EN VIVO (streamlit-webrtc)
# ============================================================

else:

    st.markdown(
        """
        <div class="custom-card">
            <div class="card-title-row">
                <div class="card-title-text">📹 Monitoreo en vivo</div>
                <div class="status-pill status-pill-active">
                    <span class="pulse-dot"></span>
                    <span>Cámara activa</span>
                </div>
            </div>
            <div class="info-box">
                📱 <b>Soporte Móvil HD:</b> Si utilizas la cámara trasera en celular y se transmite de lado, utiliza la opción <b>'Rotación de Video'</b> en la barra lateral para orientar la escena verticalmente y permitir que YOLO detecte con máxima precisión.
            </div>
        """,
        unsafe_allow_html=True
    )

    if modo_analisis == "Todos los modelos":
        st.markdown(
            """
            <div class="warning-card">
                💡 <b>Recomendación de rendimiento:</b> Utiliza el modo 'Aula' para escenas completas o 'Primer plano' para fatiga para maximizar la velocidad.
            </div>
            """,
            unsafe_allow_html=True
        )

    col_cam_cfg1, col_cam_cfg2 = st.columns(2)

    with col_cam_cfg1:
        salto_frames = st.slider(
            "Procesar un cuadro cada:",
            min_value=1,
            max_value=6,
            value=3,
            step=1,
            help="Un valor mayor reduce la carga del procesador."
        )

    with col_cam_cfg2:
        st.markdown(f"**Modo activo:** `{modo_analisis}`")
        st.markdown(f"**Sensor:** `{camara_tipo}` | **Rotación:** `{rotacion_video}`")

    class ProcesadorCamara(VideoProcessorBase):

        def __init__(
            self,
            modelos,
            confianza,
            salto_frames=3,
            device="cpu",
            imgsz=640,
            preprocesar=False,
            rotacion="Sin rotación"
        ):

            self.modelos = modelos
            self.confianza = confianza
            self.salto_frames = salto_frames
            self.device = device
            self.imgsz = imgsz
            self.preprocesar = preprocesar
            self.rotacion = rotacion
            self.numero_frame = 0
            self.ultimo_frame = None
            self.lock = threading.Lock()

        def recv(self, frame):

            imagen = frame.to_ndarray(format="bgr24")

            # Aplicar rotación según configuración de celular
            if self.rotacion == "90° Derecha":
                imagen = cv2.rotate(imagen, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotacion == "180°":
                imagen = cv2.rotate(imagen, cv2.ROTATE_180)
            elif self.rotacion == "90° Izquierda (270°)":
                imagen = cv2.rotate(imagen, cv2.ROTATE_90_COUNTERCLOCKWISE)

            if self.numero_frame % self.salto_frames == 0:

                with self.lock:

                    if self.preprocesar:
                        imagen_proc = preprocesar_frame_bgr(imagen)
                    else:
                        imagen_proc = imagen

                    # Dibujar siempre las detecciones sobre la imagen NÍTIDA ORIGINAL
                    imagen_anotada = imagen.copy()

                    for nombre_modelo, modelo in self.modelos.items():

                        try:
                            resultado = modelo.predict(
                                source=imagen_proc,
                                device=self.device,
                                imgsz=self.imgsz,
                                conf=self.confianza,
                                verbose=False
                            )[0]

                            nombres_es = obtener_nombres_espanol(
                                nombre_modelo,
                                modelo
                            )

                            resultado.names = nombres_es

                            imagen_anotada = resultado.plot(
                                img=imagen_anotada
                            )
                        except Exception:
                            pass

                    self.ultimo_frame = imagen_anotada

            self.numero_frame += 1

            salida = imagen if self.ultimo_frame is None else self.ultimo_frame

            return av.VideoFrame.from_ndarray(
                salida,
                format="bgr24"
            )

    def crear_procesador():

        return ProcesadorCamara(
            modelos=modelos_activos,
            confianza=confianza,
            salto_frames=salto_frames,
            device=device_arg,
            imgsz=tamanio_inferencia,
            preprocesar=activar_preprocesamiento,
            rotacion=rotacion_video
        )

    webrtc_streamer(
        key=f"aulas_atentas_camera_{facing_mode}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        video_processor_factory=crear_procesador,
        media_stream_constraints={
            "video": {
                "facingMode": facing_mode,
                "width": {"ideal": cam_width},
                "height": {"ideal": cam_height},
                "frameRate": {"ideal": 30}
            },
            "audio": False
        },
        async_processing=True
    )

    st.markdown("</div>", unsafe_allow_html=True)