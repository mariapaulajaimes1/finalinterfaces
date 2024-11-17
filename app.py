import paho.mqtt.client as paho
import time
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model

# Funciones MQTT
def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# Configurar colores y estilos
def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: white;
        }}
        .center-text {{
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            color: white;
        }}
        .sidebar-header {{
            color: black !important;
            font-size: 18px;
            font-weight: bold;
            
        }}
        .camera-text {{
            font-size: 20px;
            font-weight: bold;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Fondo inicial negro
set_background("#000000")

# Banner
image = Image.open('FEELIFY.BANNER.png')
st.image(image, width=1000)

# Texto centrado
st.markdown('<div class="center-text">✨ Match your music with your feelings✨ </div>', unsafe_allow_html=True)

st.subheader("No solo escucha música, ¡siente cada nota! 🎶")

# Sidebar con instrucciones
with st.sidebar:
    st.markdown('<div class="sidebar-header">✨ ¿Cómo funciona FEELIFY? ✨</div>', unsafe_allow_html=True)
    st.write("1️⃣ Haz clic en **Tomar Foto** 📸 para analizar tu estado de ánimo.")
    st.write("2️⃣ Haz clic en **Escuchar** 🎧 para descubrir tu resultado.")
    st.write("3️⃣ Confirma tu estado de ánimo con **Sí/No** 👍👎.")
    st.write("4️⃣ ¡Disfruta tu Playlist Perfecta! 🎉🎶")

# Configurar MQTT
broker = "broker.hivemq.com"
port = 1883
client1 = paho.Client("APP_CERR")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

# Cargar modelo
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Entrada de cámara
st.markdown('<div class="camera-text">¡Hola! Tómate una foto para analizar tu mood actual 😊</div>', unsafe_allow_html=True)
img_file_buffer = st.camera_input("")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer)
    img = img.resize((224, 224))
    img_array = np.array(img)

    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Ejecuta la predicción
    prediction = model.predict(data)
    print(prediction)

    # Inicializar estados
    if "estado_anterior" not in st.session_state:
        st.session_state.estado_anterior = None
    if "respuesta" not in st.session_state:
        st.session_state.respuesta = None

    # Condiciones para estados de ánimo
    if prediction[0][0] > 0.3 and st.session_state.estado_anterior != "feliz":
        st.header("😄 ¡Veo que te sientes feliz! 🎉")
        set_background("#f8ff78")  # Fondo amarillo
        st.audio("1feliz.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'feliz'}", qos=0, retain=False)
        st.session_state.estado_anterior = "feliz"
        st.session_state.respuesta = None

    elif prediction[0][1] > 0.3 and st.session_state.estado_anterior != "triste":
        st.header("😢 ¡Veo que te sientes triste! 💔")
        set_background("#7091ff")  # Fondo azul
        st.audio("1triste.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'triste'}", qos=0, retain=False)
        st.session_state.estado_anterior = "triste"
        st.session_state.respuesta = None

    elif prediction[0][2] > 0.3 and st.session_state.estado_anterior != "enojado":
        st.header("😡 ¡Veo que te sientes enojado! 🔥")
        set_background("#ed3b3b")  # Fondo rojo
        st.audio("1enojada.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'enojado'}", qos=0, retain=False)
        st.session_state.estado_anterior = "enojado"
        st.session_state.respuesta = None

    # Mostrar botones de confirmación siempre
    if st.session_state.estado_anterior in ["feliz", "triste", "enojado"]:
        st.write("❓¿Es cierto?❓")
        if st.button("✅ SÍ, así me siento"):
            st.session_state.respuesta = "si"
        if st.button("❌ NO, creo que me siento de otra manera"):
            st.session_state.respuesta = "no"

        # Reproducir canciones según la respuesta
        if st.session_state.respuesta == "si":
            if st.session_state.estado_anterior == "feliz":
                st.write("🎶 ¡Aquí tienes una canción para celebrar tu felicidad! 😄")
                st.components.v1.html(
                    """
                    <iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/album/61EvHDxTH9tvyCyFwzQLTP?utm_source=generator" 
                    width="100%" height="352" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                    loading="lazy"></iframe>
                    """, height=352)
            elif st.session_state.estado_anterior == "triste":
                st.write("🎶 Esta canción te acompañará en tu momento 💙.")
                st.components.v1.html(
                    """
                    <iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/playlist/37i9dQZF1DX1wBZWxWB0O1?utm_source=generator" 
                    width="100%" height="352" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                    loading="lazy"></iframe>
                    """, height=352)
            elif st.session_state.estado_anterior == "enojado":
                st.write("🎶 ¡Desahógate con esta canción potente! 🔥")
                st.components.v1.html(
                    """
                    <iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/playlist/7iVI3u03k78JvGu8YaOKR2?utm_source=generator" 
                    width="100%" height="352" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                    loading="lazy"></iframe>
                    """, height=352)
        elif st.session_state.respuesta == "no":
            st.write("🎵 Está bien, aquí tienes algo neutral para escuchar. 🤗")
            st.components.v1.html(
                """
                <iframe style="border-radius:12px" 
                src="https://open.spotify.com/embed/playlist/37i9dQZF1EVHGWrwldPRtj?utm_source=generator" 
                width="100%" height="352" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                loading="lazy"></iframe>
                """, height=352)
