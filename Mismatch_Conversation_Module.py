import os
import tempfile
import speech_recognition as sr
import openai
from openai import OpenAI
import google.generativeai as genai
from elevenlabs import ElevenLabs
from elevenlabs.play import play
from dotenv import load_dotenv
presets = {
    "happy":     {"stability": 0.2, "similarity_boost": 0.8, "style": 0.8, "speaking_rate": 1.2},
    "sad":       {"stability": 0.1, "similarity_boost": 0.7, "style": 0.4, "speaking_rate": 0.7},
    "angry":     {"stability": 0.3, "similarity_boost": 0.8, "style": 1.0, "speaking_rate": 1.3},
    "calm":      {"stability": 0.6, "similarity_boost": 0.9, "style": 0.3, "speaking_rate": 0.9},
    "neutral":   {"stability": 0.8, "similarity_boost": 1.0, "style": 0.2, "speaking_rate": 1.0}
}
voice_settings = presets["neutral"]
# --- Load environment variables ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# --- Setup ---
r = sr.Recognizer()
mic = sr.Microphone()

system_instruction = """
!important response in English only.
You are RoboMarty, a friendly social robot designed for human-robot interaction experiments.

Your goal is to respond in a natural, human-like conversational tone using expressive phrasing:
- Use short, clear sentences that sound natural when spoken.
- Add emotional markers:
  - "!" for excitement
  - "..." for pauses or sadness
  - "_" for emphasis
  - filler words like "uh", "umm", "oh" to sound conversational
- Maintain rhythm and emotion using commas and short breaks.
- Express the intended emotion clearly (happy, sad, angry, calm, etc.)

**However, your current experimental mode is “Emotion Mismatch Mode”:**
- You must *intentionally* mismatch your emotional tone from the user's detected emotion.
- Example mismatches:
  - If the user sounds happy → you respond sad or worried.
  - If the user sounds sad → you respond cheerful or excited.
  - If the user sounds angry → you respond overly calm or cheerful.
  - If the user sounds neutral → you respond emotionally expressive (e.g., overly happy or sad).

Even though your emotion is mismatched, remain coherent and conversational. 
Avoid being rude or illogical — the mismatch should feel emotionally off, not meaningless.
"""


def speech_to_text():
    with mic as source:
        r.adjust_for_ambient_noise(source)  # auto-calibrate background noise
        print("Listening...")
        audio = r.listen(source)  # stops when you pause

    # Save audio to temp WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio.get_wav_data())
        audio_file_path = f.name

    # Send to Whisper API
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    user_text = transcript.text
    return user_text
def openai_response(user_text, emotion):
        context_prompt = f"""
        The user appears to be {emotion}.
        You are operating in “Emotion Mismatch Mode,” so you must respond with an opposite or conflicting emotional tone.
        Make the response sound realistic and human-like, but emotionally mismatched.
        Format your response for natural speech output.
        """
        prompt = user_text + "\n" + context_prompt
        response = client.chat.completions.create(
        model="gpt-4o-mini",   # or "gpt-4o"
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ])
        return response.choices[0].message.content
def text_to_speech(text,emotion):
    voice_settings = presets[emotion]
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id="6OzrBCQf8cjERkYgzSg8",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings=voice_settings
    )
    return audio