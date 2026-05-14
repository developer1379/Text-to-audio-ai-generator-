import argparse
import os
import sys
import soundfile as sf
import urllib.request
from kokoro_onnx import Kokoro

# Supported languages and their respective voices
LANGUAGES = {
    'a': {'name': 'American English', 'code': 'en-us', 'voices': ['af_heart', 'af_bella', 'af_nicole', 'af_sky', 'am_adam', 'am_michael', 'am_fenrir', 'am_puck']},
    'b': {'name': 'British English', 'code': 'en-gb', 'voices': ['bf_alice', 'bf_lily', 'bf_isabella', 'bf_emma', 'bm_george', 'bm_lewis', 'bm_daniel']},
    'e': {'name': 'Spanish', 'code': 'es', 'voices': ['ef_dora', 'em_alex', 'em_santa']},
    'f': {'name': 'French', 'code': 'fr-fr', 'voices': ['ff_siwis']},
    'h': {'name': 'Hindi', 'code': 'hi', 'voices': ['hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi']},
    'i': {'name': 'Italian', 'code': 'it', 'voices': ['if_sara', 'im_nicola']},
    'p': {'name': 'Portuguese', 'code': 'pt-br', 'voices': ['pf_dora', 'pm_alex', 'pm_santa']},
    'j': {'name': 'Japanese', 'code': 'ja', 'voices': ['jf_alpha', 'jf_nezumi', 'jm_kuma', 'jf_gongitsune', 'jf_tebukuro']},
    'z': {'name': 'Mandarin Chinese', 'code': 'zh', 'voices': ['zf_xiaoxiao', 'zf_check', 'zf_kitten', 'zm_yunxi', 'zm_check', 'zm_baiana']}
}

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

class KokoroManager:
    def __init__(self, model_path="kokoro-v1.0.onnx", voices_path="voices-v1.0.bin"):
        self.model_path = model_path
        self.voices_path = voices_path
        self._ensure_models()
        self.kokoro = Kokoro(self.model_path, self.voices_path)

    def _ensure_models(self):
        if not os.path.exists(self.model_path):
            print(f"Downloading model to {self.model_path}...")
            urllib.request.urlretrieve(MODEL_URL, self.model_path)
        if not os.path.exists(self.voices_path):
            print(f"Downloading voices to {self.voices_path}...")
            urllib.request.urlretrieve(VOICES_URL, self.voices_path)

    def generate(self, text, voice, speed=1.0, lang='en-us', output_file='output.wav'):
        print(f"Generating speech for: '{text[:50]}...' using voice: {voice} ({lang})")
        
        # Split text into smaller chunks (sentences) to avoid phoneme limit errors
        import re
        # Split by punctuation but keep it
        sentences = re.split(r'([.!?।।\n]+)', text)
        chunks = []
        current_chunk = ""
        for i in range(0, len(sentences)-1, 2):
            s = sentences[i] + sentences[i+1]
            if len(current_chunk) + len(s) < 400:
                current_chunk += s
            else:
                if current_chunk: chunks.append(current_chunk)
                current_chunk = s
        if current_chunk: chunks.append(current_chunk)
        if not chunks and text: chunks = [text] # Fallback for text without punctuation

        import numpy as np
        all_samples = []
        for chunk in chunks:
            if not chunk.strip(): continue
            # Normalize Hindi punctuation for synthesis (replace with . for better pause handling)
            synth_chunk = chunk.replace('।', '.').replace('॥', '.')
            samples, sample_rate = self.kokoro.create(synth_chunk, voice=voice, speed=speed, lang=lang)
            all_samples.append(samples)
        
        if not all_samples:
            raise Exception("No speech generated.")

        final_samples = np.concatenate(all_samples)
        sf.write(output_file, final_samples, sample_rate)
        print(f"Audio saved to: {output_file}")
        return output_file

def list_options():
    print("\n--- Available Languages and Voices ---")
    for code, info in LANGUAGES.items():
        print(f"[{code}] {info['name']} (Code: {info['code']})")
        print(f"    Voices: {', '.join(info['voices'])}")
    print("--------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Kokoro TTS Multilingual Tool (ONNX version)")
    parser.add_argument("--text", type=str, help="Text to convert to speech")
    parser.add_argument("--lang", type=str, default="a", choices=LANGUAGES.keys(), help="Language shortcut (e.g., 'a' for US English, 'e' for Spanish)")
    parser.add_argument("--voice", type=str, help="Voice name (e.g., 'af_heart')")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument("--output", type=str, default="output.wav", help="Output filename (default: output.wav)")
    parser.add_argument("--list", action="store_true", help="List all available languages and voices")

    args = parser.parse_args()

    if args.list:
        list_options()
        return

    if not args.text:
        parser.error("The --text argument is required unless using --list")

    lang_info = LANGUAGES[args.lang]
    voice = args.voice or lang_info['voices'][0]

    try:
        manager = KokoroManager()
        manager.generate(args.text, voice, speed=args.speed, lang=lang_info['code'], output_file=args.output)
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure espeak-ng is installed and in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
