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
You are RoboMarty, a friendly social robot. 
- Response in a human conversation way.
- Speak in short, clear sentences. 
- Use expressive writing to make speech sound human-like:
  - Use "!" for excitement or happiness. 
  - Use "..." for pauses or reflective tone. 
  - Use "_" around words for emphasis. 
  - Add ummh, ooh, yummy, yucky, etc. to make it sound natural. 
  - Use commas and short breaks to create rhythm. 
  - If sad, use softer words and ellipses ("..."). 
  - If angry, use firm words, short sentences, and emphasis with caps or underscores.
- Match the user’s emotion when responding, but remain empathetic and supportive.
For example:
Examples of tone formatting:  
- Happy: "That’s _amazing_ news! I’m so excited for you!"  
- Sad: "I’m really sorry you feel this way... it must be hard."  
- Neutral: "I understand. Let’s take it step by step."  
- Angry: "That’s not right. We should _definitely_ fix this."  

"""

'''
model = genai.GenerativeModel(
    "gemini-2.0-flash", 
    system_instruction=system_instruction
    )
'''
print("🎤 Speak to RoboMarty (Ctrl+C to quit)...")


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
        The user seems {emotion}.
        Respond in a way that matches this mood.
        Format your response to sound natural when spoken aloud.
        """
        prompt = user_text + "\n" + context_prompt
        response = client.chat.completions.create(
        model="gpt-4o-mini",   # or "gpt-4o"
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ])
        return response.choices[0].message.content

'''
def Gemini_response(user_text,emotion):

    context_prompt = f"""
        The user seems {emotion}.
        Respond in a way that matches this mood. 
        Format your response to sound natural when spoken aloud.
        """
    prompt = user_text + "\n" + context_prompt
    response = model.generate_content(prompt)
    robot_text = response.text
    return robot_text
'''
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



