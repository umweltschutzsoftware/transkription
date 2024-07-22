import streamlit as st
from openai import OpenAI
import os
from io import BytesIO
import hmac
import streamlit as st
import pyperclip

st.set_page_config(page_title="Transkription", page_icon="🎤", layout="centered", initial_sidebar_state="collapsed")

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("Falsches Passwort. Bitte erneut eingeben.")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Function to transcribe audio using OpenAI's API
@st.cache_data
def transcribe_audio(audio_file):
    client = OpenAI(api_key=st.secrets["key"])
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
    )
    return transcription.text

# Function to call the OpenAI API to use chatgpt to format the text
@st.cache_data
def format_text(text):
    client = OpenAI(api_key=st.secrets["key"])
    formatted_text = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein Rechtsanwaltsfachangestellter und formatierst den Text. Der Text soll später in Branchensoftware weiterverwendet werden. Die Eingabe ist die Transkription einer Audiodatei. Der grundsätzliche Text soll vollständig überführt werden, d.h. unverändert erhalten bleiben. Formatiere Aufzählungspunkte, sodass ganze Zahlen den jeweiligen Punkten vorangestellt sind. Bitte achte auf Rechtschreibung und Grammatik. Beachte auf die korrekte Bezeichnung der Rechtsprechung. Stelle Satzzeichen die diktiert wurden als Zeichen dar. Stelle die Formatierung so dar, dass das Dokument direkt in eine word datei kopiert werden kann."},
            {"role": "user", "content": text},
        ],
    )
    return formatted_text.choices[0].message.content

# Streamlit app
st.title("Audio Transkriptions App")
st.write("Lade eine Audiodatei hoch und bekomme eine Transkription. Diese App nutzt die OpenAI Speech-to-Text Schnittstelle.")
st.write("Die maximale Dateigröße beträgt 2 MB.")
st.write("Die Anwendung wird zur Verfügung gestellt durch das Ingenieurbüro Richters & Hüls in Ahaus.")
# Audio file upload
uploaded_file = st.file_uploader("Audiodatei auswählen", type=["mp3", "wav", "m4a"])
transcription = None
formatted_text = None

if uploaded_file is not None:
    file_size = uploaded_file.size
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        st.error(f"Die Dateigröße überschreitet das aktuelle Limit von {max_size_mb}MB. Bitte eine kleinere Datei hochladen.")
    else:
        st.info("Die Daten werden transkribiert. Bitte warten...")
        transcription = transcribe_audio(uploaded_file)
        st.info("Es wird ein Formatierungsvorschlag erstellt. Bitte warten...")
        formatted_text = format_text(transcription)

        st.text_area("Transkription", transcription, disabled=True, height=300)
        st.text_area("Formatierungsvorschlag", formatted_text, disabled=True, height=300)
        # Kopiere den text in die Zwischenablage
        st.write("Für eine Weiterverarbeitng kann der Text in die Zwischenablage kopiert werden.")
        # Kopiere den text in die Zwischenablage
        if st.button("In Zwischenablage kopieren"):
            pyperclip.copy(formatted_text)
            st.success("Text erfolgreich in die Zwischenablage kopiert!")