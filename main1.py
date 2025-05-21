import streamlit as st
import speech_recognition as sr
import os
import logging
from lang_utils import detect_language, get_language_name, text_to_speech
import pygame
import tempfile
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize pygame for audio playback
pygame.mixer.init()

# Set page configuration
st.set_page_config(
    page_title="Voice-Text Converter",
    page_icon="🎙️",
    layout="wide"
)

def main():
    st.title("Voice-Text Converter (Indian Languages)")
    st.write("Convert speech to text and text to speech with language detection")

    # Initialize session state
    if 'text' not in st.session_state:
        st.session_state.text = ""
    if 'detected_language' not in st.session_state:
        st.session_state.detected_language = "None"

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Text area
        st.subheader("Converted Text")
        text_area = st.text_area(
            "Text will appear here...",
            value=st.session_state.text,
            height=200,
            key="text_area"
        )
        st.session_state.text = text_area

        # Language display
        st.write(f"Detected Language: {st.session_state.detected_language}")

    with col2:
        # Controls
        st.subheader("Controls")
        
        # Voice to Text button
        if st.button("🎙️ Voice to Text", use_container_width=True):
            with st.spinner("Listening..."):
                voice_to_text()

        # Text to Voice button
        if st.button("🔊 Text to Voice", use_container_width=True):
            if st.session_state.text.strip():
                with st.spinner("Processing..."):
                    text_to_voice(st.session_state.text)
            else:
                st.warning("Please enter text or convert voice to text first.")

        # Clear button
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.text = ""
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

def text_to_voice(text):
    """Convert text to voice and play the audio."""
    try:
        # Detect language
        lang_code = detect_language(text)
        lang_name = get_language_name(lang_code)

        # Update detected language
        st.session_state.detected_language = lang_name

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            output_file = temp_file.name

        # Convert text to speech
        result = text_to_speech(text, lang_code, output_file)

        # Check if result is a tuple (success, method) or just a boolean
        if isinstance(result, tuple) and len(result) == 2:
            success, method = result
        else:
            # If result is just a boolean, assume gTTS was used if successful
            success = result
            method = 'gtts' if success else None

        if success:
            if method == 'gtts':
                if os.path.exists(output_file):
                    # Display audio player
                    audio_file = open(output_file, 'rb')
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3')
                    st.success("Text converted to speech successfully!")
                    
                    # Clean up
                    audio_file.close()
                    os.unlink(output_file)
                else:
                    st.error("Audio file was not generated.")
            elif method == 'pyttsx3':
                st.info("Text-to-speech completed using offline engine (pyttsx3).")
        else:
            st.error("Failed to convert text to speech.")
    except Exception as e:
        logging.error(f"Error in text-to-voice process: {e}")
        st.error(f"An error occurred: {e}")
        result = text_to_speech(text, lang_code, output_file)
        st.write(f"Debug: text_to_speech returned: {result}")
        
if __name__ == "__main__":
    main()