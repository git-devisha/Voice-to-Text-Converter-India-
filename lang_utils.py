from langdetect import detect
from gtts import gTTS

# Mapping of Indian languages to their language codes (for gTTS and speech recognition)
INDIAN_LANGUAGES = {
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'ur': 'Urdu',
    'gu': 'Gujarati',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'or': 'Odia',
    'pa': 'Punjabi',
    'as': 'Assamese',
    'si': 'Sinhala',
    'en': 'English'  # Fallback for non-Indian languages
}

def detect_language(text):
    """Detect the language of the given text."""
    try:
        lang_code = detect(text)
        return lang_code if lang_code in INDIAN_LANGUAGES else 'en'
    except:
        return 'en'

def get_language_name(lang_code):
    """Get the full name of the language from its code."""
    return INDIAN_LANGUAGES.get(lang_code, 'Unknown')

def text_to_speech(text, lang_code, output_file='output.mp3'):
    """Convert text to speech and save as an audio file."""
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(output_file)
        return True
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return False