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

# Configurar colores según el estado
def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
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

st.title("🎵 Match your music with your feelings 💖")
st.subheader("No solo escucha música, ¡siente cada nota! 🎶")

# Sidebar con instrucciones
with st.sidebar:
    st.subheader("✨ ¿Cómo funciona FEELIFY? ✨")
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
img_file_buffer = st.camera_input("¡Hola! Tómate una foto para analizar tu mood actual 😊")

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
        set_background("#FFD700")  # Fondo amarillo
        st.audio("1feliz.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'feliz'}", qos=0, retain=False)
        st.session_state.estado_anterior = "feliz"
        st.session_state.respuesta = None

    elif prediction[0][1] > 0.3 and st.session_state.estado_anterior != "triste":
        st.header("😢 ¡Veo que te sientes triste! 💔")
        set_background("#1E90FF")  # Fondo azul
        st.audio("1triste.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'triste'}", qos=0, retain=False)
        st.session_state.estado_anterior = "triste"
        st.session_state.respuesta = None

    elif prediction[0][2] > 0.3 and st.session_state.estado_anterior != "enojado":
        st.header("😡 ¡Veo que te sientes enojado! 🔥")
        set_background("#FF4500")  # Fondo rojo
        st.audio("1enojada.mp3", format="audio/mp3", start_time=0)
        client1.publish("misabela", "{'gesto': 'enojado'}", qos=0, retain=False)
        st.session_state.estado_anterior = "enojado"
        st.session_state.respuesta = None

    # Confirmación del estado
    if st.session_state.estado_anterior in ["feliz", "triste", "enojado"]:
        if st.session_state.respuesta is None:
            st.write("❓ ¿Es cierto?")
            if st.button("✅ SÍ, así me siento"):
                st.session_state.respuesta = "si"
            elif st.button("❌ NO, creo que me siento de otra manera"):
                st.session_state.respuesta = "no"

        # Reproducir según respuesta
        if st.session_state.respuesta == "si":
            if st.session_state.estado_anterior == "feliz":
                st.write("🎶 ¡Aquí tienes una canción para celebrar tu felicidad! 😄")
                st.audio("cancionfeliz.mp3", format="audio/mp3", start_time=0)
            elif st.session_state.estado_anterior == "triste":
                st.write("🎶 Esta canción te acompañará en tu momento 💙.")
                st.audio("canciontriste.mp3", format="audio/mp3", start_time=0)
            elif st.session_state.estado_anterior == "enojado":
                st.write("🎶 ¡Desahógate con esta canción potente! 🔥")
                st.audio("cancionenojado.mp3", format="audio/mp3", start_time=0)
        elif st.session_state.respuesta == "no":
            st.write("🎵 Está bien, aquí tienes algo neutral para escuchar. 🤗")
            st.audio("neutro.mp3", format="audio/mp3", start_time=0)
