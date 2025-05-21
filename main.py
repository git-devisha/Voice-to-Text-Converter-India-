import tkinter as tk
from tkinter import messagebox, scrolledtext
import speech_recognition as sr
import os
import threading
import logging
from lang_utils import detect_language, get_language_name, text_to_speech
import pygame  # For playing audio files

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize pygame for audio playback
pygame.mixer.init()

class VoiceTextConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice-Text Converter (Indian Languages)")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        # Recognizer for speech-to-text
        self.recognizer = sr.Recognizer()

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        """Create the GUI elements."""
        # Title Label
        title_label = tk.Label(self.root, text="Voice-Text Converter", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        # Text Area for displaying converted text
        self.text_area = scrolledtext.ScrolledText(self.root, width=50, height=10, font=("Arial", 12))
        self.text_area.pack(pady=10)

        # Language Label to display detected language
        self.language_label = tk.Label(self.root, text="Detected Language: None", font=("Arial", 10), bg="#f0f0f0")
        self.language_label.pack(pady=5)

        # Buttons Frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Voice to Text Button
        self.voice_to_text_btn = tk.Button(button_frame, text="Voice to Text", font=("Arial", 12), command=self.start_voice_to_text, bg="#4CAF50", fg="white")
        self.voice_to_text_btn.grid(row=0, column=0, padx=10)

        # Text to Voice Button
        self.text_to_voice_btn = tk.Button(button_frame, text="Text to Voice", font=("Arial", 12), command=self.start_text_to_voice, bg="#2196F3", fg="white")
        self.text_to_voice_btn.grid(row=0, column=1, padx=10)

        # Clear Button
        self.clear_btn = tk.Button(button_frame, text="Clear", font=("Arial", 12), command=self.clear_text, bg="#f44336", fg="white")
        self.clear_btn.grid(row=0, column=2, padx=10)

    def start_voice_to_text(self):
        """Start the voice-to-text conversion in a separate thread."""
        self.text_area.delete(1.0, tk.END)
        self.language_label.config(text="Detected Language: Listening...")
        threading.Thread(target=self.voice_to_text, daemon=True).start()

    def voice_to_text(self):
        """Convert voice to text and detect language."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5)

            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            if text:
                # Detect language
                lang_code = detect_language(text)
                lang_name = get_language_name(lang_code)

                # Update GUI
                self.text_area.insert(tk.END, text)
                self.language_label.config(text=f"Detected Language: {lang_name}")
            else:
                messagebox.showerror("Error", "Could not understand the audio.")
        except sr.WaitTimeoutError:
            messagebox.showerror("Error", "Listening timed out. Please try again.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand the audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results; {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def start_text_to_voice(self):
        """Start the text-to-voice conversion in a separate thread."""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text or convert voice to text first.")
            return

        self.language_label.config(text="Detected Language: Processing...")
        threading.Thread(target=self.text_to_voice, args=(text,), daemon=True).start()

    def text_to_voice(self, text):
        """Convert text to voice and play the audio."""
        try:
            # Detect language
            lang_code = detect_language(text)
            lang_name = get_language_name(lang_code)

            # Update GUI
            self.language_label.config(text=f"Detected Language: {lang_name}")

            # Convert text to speech
            output_file = "output.mp3"
            success, method = text_to_speech(text, lang_code, output_file)

            if success:
                if method == 'gtts':
                    # Play the audio file
                    if os.path.exists(output_file):
                        pygame.mixer.music.load(output_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        logging.info("Audio playback completed.")
                    else:
                        messagebox.showerror("Error", "Audio file was not generated.")
                elif method == 'pyttsx3':
                    messagebox.showinfo("Info", "Text-to-speech completed using offline engine (pyttsx3).")
            else:
                messagebox.showerror("Error", "Failed to convert text to speech using both gTTS and pyttsx3.")
        except Exception as e:
            logging.error(f"Error in text-to-voice process: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_text(self):
        """Clear the text area and reset language label."""
        self.text_area.delete(1.0, tk.END)
        self.language_label.config(text="Detected Language: None")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTextConverterApp(root)
    root.mainloop()