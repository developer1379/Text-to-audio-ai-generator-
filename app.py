import gradio as gr
import os
from kokoro_tool import KokoroManager, LANGUAGES

# Initialize manager (will download models on first load)
manager = None

def get_manager():
    global manager
    if manager is None:
        manager = KokoroManager()
    return manager

def tts_interface(text, lang_shortcut, voice, speed):
    try:
        m = get_manager()
        lang_info = LANGUAGES[lang_shortcut]
        
        # Generate audio
        output_path = "web_output.wav"
        m.generate(text, voice, speed, lang_info['code'], output_path)
        
        return output_path
    except Exception as e:
        raise gr.Error(f"Error: {str(e)}. Please ensure espeak-ng is installed and in your PATH.")

def update_voices(lang_shortcut):
    voices = LANGUAGES[lang_shortcut]['voices']
    return gr.Dropdown(choices=voices, value=voices[0])

# Custom CSS for "Premium" look
custom_css = """
footer {visibility: hidden}
.gradio-container {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white !important;
}
.header-box {
    text-align: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.header-box h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
button.primary {
    background: linear-gradient(90deg, #0ea5e9, #6366f1) !important;
    border: none !important;
}
"""

with gr.Blocks(css=None, theme=None) as demo:
    with gr.Column(elem_classes="header-box"):
        gr.Markdown("# 🎙️ Kokoro Multilingual TTS (ONNX)")
        gr.Markdown("High-quality, lightweight speech generation across 9 languages.")

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Enter Text",
                placeholder="Hello, welcome to Kokoro TTS. How can I help you today?",
                lines=5,
                elem_id="text-input"
            )
            
            with gr.Row():
                lang_dropdown = gr.Dropdown(
                    choices=[(info['name'], code) for code, info in LANGUAGES.items()],
                    value='a',
                    label="Language"
                )
                voice_dropdown = gr.Dropdown(
                    choices=LANGUAGES['a']['voices'],
                    value='af_heart',
                    label="Voice"
                )
            
            speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.1, label="Speed")
            
            generate_btn = gr.Button("Generate Speech", variant="primary", elem_classes="primary")

        with gr.Column(scale=1):
            audio_output = gr.Audio(label="Generated Speech", type="filepath")
            gr.Markdown("### 💡 Notes")
            gr.Markdown("- **First Run**: Downloading model files (~100MB) may take a moment.")
            gr.Markdown("- **System Requirement**: You MUST have `espeak-ng` installed and in your PATH.")
            gr.Markdown("- **All Languages Supported**: English, Spanish, French, Hindi, Italian, Portuguese, Japanese, and Mandarin Chinese.")

    # Event Handlers
    lang_dropdown.change(fn=update_voices, inputs=lang_dropdown, outputs=voice_dropdown)
    generate_btn.click(
        fn=tts_interface,
        inputs=[text_input, lang_dropdown, voice_dropdown, speed_slider],
        outputs=audio_output
    )

if __name__ == "__main__":
    demo.launch(css=custom_css, theme=gr.themes.Soft(primary_hue="sky"))
