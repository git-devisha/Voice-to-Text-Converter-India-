import streamlit as st
import speech_recognition as sr
import os
import logging
from lang_utils import detect_language, get_language_name, text_to_speech
import tempfile
import pyttsx3
from deep_translator import GoogleTranslator

# Set page configuration
st.set_page_config(
    page_title="Voice-Text Converter",
    page_icon="🎙️",
    layout="wide"
)


# Inject CSS styles
st.markdown(
    """
    <style>
    /* Change background color */
    .stApp {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
    }
    div.stButton > button {
        background-color: #fac543;  /* Green background */
        color: black;                /* White text */
        font-size: 18px;             /* Bigger font */
        padding: 10px 24px;
        border-radius: 12px;         /* Rounded corners */
        border: none;
        transition: background-color 0.3s ease;
    }

    /* Button hover effect */
    div.stButton > button:hover {
        background-color: #ff6901;
        colo
        cursor: pointer;
    }

    /* Style the radio button label */
    .stRadio > div > label {
        font-size: 18px;
        color: #007acc;
        font-weight: bold;
        align-items:right;
    }

    /* Style selected radio option */
    .stRadio > div > div > div[aria-checked="true"] {
        background-color: #d0e7ff;
        border-radius: 5px;
    }

    /* Example: style headers */
    h1 {
        color: #3a3a3a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Supported languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Accessibility feedback handler
def speak_feedback(message):
    mode = st.session_state.get("accessibility_mode", "Default")
    if mode == "Blind":
        try:
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            st.warning(f"TTS error: {e}")
    elif mode == "Deaf":
        st.info("🔔 " + message)

def main():
    st.title("🎙️ Voice-Text Converter for Deaf & Blind Users")

    # Accessibility selector
    accessibility_mode = st.radio(
    "Select Accessibility Mode:",
    ["Default", "Deaf", "Blind"],
    index=0  # Default selected
)
    st.session_state.accessibility_mode = accessibility_mode

    # Session state initialization
    st.session_state.setdefault("text", "")
    st.session_state.setdefault("translated_text", "")
    st.session_state.setdefault("detected_language", "None")

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Original Text")
        st.session_state.text = st.text_area(
            "Text will appear here...",
            value=st.session_state.text,
            height=68
        )

        st.subheader("Translated Text")
        st.text_area(
            "Translated text will appear here...",
            value=st.session_state.translated_text,
            height=68,
            disabled=True
        )

        st.write(f"Detected Language: {st.session_state.detected_language}")

    with col2:
        st.subheader("Controls")

        if st.button("🎙️ Voice to Text", use_container_width=True):
            with st.spinner("Listening..."):
                voice_to_text()

        st.subheader("Translation & Text to Voice Settings")
        selected_language = st.selectbox(
            "Select Target Language",
            list(SUPPORTED_LANGUAGES.keys())
        )

        if st.button("🌐 Translate", use_container_width=True):
            if st.session_state.text.strip():
                with st.spinner("Translating..."):
                    translate_text(st.session_state.text, selected_language)
            else:
                st.warning("Please provide some input text first.")

        if st.button("🔊 Text to Voice", use_container_width=True):
            if st.session_state.translated_text.strip():
                with st.spinner("Generating speech..."):
                    text_to_voice(st.session_state.translated_text, selected_language)
            else:
                st.warning("Please translate the text first.")

        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.text = ""
            st.session_state.translated_text = ""
            st.session_state.detected_language = "None"
            st.rerun()

def voice_to_text():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)

        text = recognizer.recognize_google(audio)
        lang_code = detect_language(text)
        lang_name = get_language_name(lang_code)

        st.session_state.text = text
        st.session_state.detected_language = lang_name
        st.session_state.translated_text = ""

        msg = "Speech converted to text successfully!"
        st.success(msg)
        speak_feedback(msg)
        st.rerun()

    except sr.WaitTimeoutError:
        st.error("Listening timed out.")
    except sr.UnknownValueError:
        st.error("Could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")

def translate_text(text, selected_language):
    try:
        lang_code = SUPPORTED_LANGUAGES.get(selected_language, "en")
        translated = GoogleTranslator(source='auto', target=lang_code).translate(text)

        st.session_state.translated_text = translated
        msg = f"Text translated to {selected_language} successfully!"
        st.success(msg)
        speak_feedback(msg)
        st.rerun()

    except Exception as e:
        st.error(f"Translation error: {e}")

def text_to_voice(text, selected_language):
    try:
        lang_code = SUPPORTED_LANGUAGES.get(selected_language, "en")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            output_file = temp_file.name

        result = text_to_speech(text, lang_code, output_file)

        if isinstance(result, tuple) and result[0]:
            with open(output_file, 'rb') as audio_file:
                st.audio(audio_file.read(), format='audio/mp3')
            os.unlink(output_file)
            msg = f"Text converted to speech in {selected_language}."
            st.success(msg)
            speak_feedback(msg)
        else:
            st.error("Speech synthesis failed.")
    except Exception as e:
        st.error(f"TTS Error: {e}")

if __name__ == "__main__":
    main()
