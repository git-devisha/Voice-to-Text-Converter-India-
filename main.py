import streamlit as st
import speech_recognition as sr
import os
import logging
from lang_utils import detect_language, get_language_name, text_to_speech
import tempfile
import time
from deep_translator import GoogleTranslator
# from googletrans import Translator, LANGUAGES
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page configuration
st.set_page_config(
    page_title="Voice-Text Converter",
    page_icon="🎙️",
    layout="wide"
)

# Initialize translator
translator = GoogleTranslator()

# List of supported languages for gTTS and Google Translate
# Format: { "Language Name": "language_code" }
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

def main():
    st.title("Voice-Text Converter (Indian Languages)")
    st.write("Convert speech to text, translate to a selected language, and convert to speech")

    # Initialize session state
    if 'text' not in st.session_state:
        st.session_state.text = ""
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
    if 'detected_language' not in st.session_state:
        st.session_state.detected_language = "None"

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Original text area
        st.subheader("Original Text")
        text_area = st.text_area(
            "Text will appear here...",
            value=st.session_state.text,
            height=200,
            key="text_area"
        )
        st.session_state.text = text_area

        # Translated text area
        st.subheader("Translated Text")
        translated_text_area = st.text_area(
            "Translated text will appear here...",
            value=st.session_state.translated_text,
            height=200,
            key="translated_text_area",
            disabled=True  # Make it read-only
        )

        # Language display
        st.write(f"Detected Language: {st.session_state.detected_language}")

    with col2:
        # Controls
        st.subheader("Controls")
        
        # Voice to Text button
        if st.button("🎙️ Voice to Text", use_container_width=True):
            with st.spinner("Listening..."):
                voice_to_text()

        # Language selection for Translation and Text to Voice
        st.subheader("Translation & Text to Voice Settings")
        selected_language = st.selectbox(
            "Select Target Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            index=0  # Default to English
        )

        # Translate button
        if st.button("🌐 Translate", use_container_width=True):
            if st.session_state.text.strip():
                with st.spinner("Translating..."):
                    translate_text(st.session_state.text, selected_language)
            else:
                st.warning("Please enter text or convert voice to text first.")

        # Text to Voice button
        if st.button("🔊 Text to Voice", use_container_width=True):
            if st.session_state.translated_text.strip():
                with st.spinner("Processing..."):
                    text_to_voice(st.session_state.translated_text, selected_language)
            else:
                st.warning("Please translate the text first.")

        # Clear button
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.text = ""
            st.session_state.translated_text = ""
            st.session_state.detected_language = "None"
            st.rerun()

def voice_to_text():
    """Convert voice to text and detect language."""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)

        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio)
        if text:
            # Detect language
            lang_code = detect_language(text)
            lang_name = get_language_name(lang_code)

            # Update session state
            st.session_state.text = text
            st.session_state.detected_language = lang_name
            st.session_state.translated_text = ""  # Clear translated text
            st.success("Speech converted successfully!")
            st.rerun()
        else:
            st.error("Could not understand the audio.")
    except sr.WaitTimeoutError:
        st.error("Listening timed out. Please try again.")
    except sr.UnknownValueError:
        st.error("Could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

from deep_translator import GoogleTranslator


def translate_text(text, selected_language):
    try:
        # Convert "Hindi" -> "hi"
        lang_code = SUPPORTED_LANGUAGES.get(selected_language, "en")

        # Use lang_code with GoogleTranslator
        translated = GoogleTranslator(source='auto', target=lang_code).translate(text)

        st.session_state.translated_text = translated
        st.success(f"Text translated to {selected_language} successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred during translation: {e}")

def text_to_voice(text, selected_language):
    try:
        # Get the language code for selected language
        lang_code = SUPPORTED_LANGUAGES.get(selected_language, "en")

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            output_file = temp_file.name

        # Convert text to speech
        result = text_to_speech(text, lang_code, output_file)

        # Check result and play
        if isinstance(result, tuple) and result[0]:
            with open(output_file, 'rb') as audio_file:
                st.audio(audio_file.read(), format='audio/mp3')
            st.success(f"Spoken in {selected_language} ({lang_code})")
            os.unlink(output_file)
        else:
            st.error(f"TTS failed for language: {selected_language} ({lang_code})")
    except Exception as e:
        st.error(f"Error in TTS: {e}")
    print(f"Selected: {selected_language}, Lang Code: {lang_code}, Text: {text}")

if __name__ == "__main__":
    main()