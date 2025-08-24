# 8D Audio Converter 🎧  

## 🔄 Modernized Version of the Project

This is a **modernized version** of the original [8D-Audio by maxgillham](https://github.com/maxgillham/8D-Audio), using more up-to-date technologies and improved audio processing. Key differences include:

- **Using `yt-dlp`** instead of `youtube-dl` for more efficient audio downloads from YouTube.
- Audio processing implemented with **PyTorch and Torchaudio**, replacing older libraries.
- Integration of **FFmpeg** for audio file conversion and manipulation.
- Inclusion of a test tool to visualize and verify the applied stereo effect.

You can compare both versions here:

- [Original version by maxgillham](https://github.com/maxgillham/8D-Audio)
- [Modernized version](https://github.com/JosuedGarm52/8D-Audio)


## APP

A simple Flask web app that lets you download any song from YouTube and apply a simulated **8D Audio effect** (stereo panning + light effects).  

Unlike the original version of this project, this fork has been updated to:  
- Use **`yt-dlp`** (instead of the outdated `youtube-dl`).  
- Work with **PyTorch + Torchaudio** for modern audio processing.  
- Include **FFmpeg integration** for audio conversion.  
- Provide a small **test utility** to visualize and confirm stereo effects.  

---

## ⚡ Features  
- Download audio directly from YouTube.  
- Apply a simple **8D effect** (continuous stereo panning).  
- Normalize and slightly enhance the sound.  
- Serve the processed audio file through a Flask web interface.  
- Test script to visualize left/right channels and confirm the effect.  

---

## 🚀 Getting Started  

### 1. Clone the repository  
```bash
git clone https://github.com/JosuedGarm52/8D-Audio.git
cd 8D-Audio
```

### 2. Install FFmpeg  
This project requires **FFmpeg** (for conversion and metadata).  

- Download FFmpeg from [ffmpeg.org/download](https://www.ffmpeg.org/download.html).  
- Extract it and place it somewhere like `C:\ffmpeg\bin`.  
- Update `config.py` with the correct path:  

```python
# config.py
FFMPEG_PATH = r"C:\ffmpeg\bin"

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'ffmpeg_location': FFMPEG_PATH
}
```

On Linux/macOS, make sure `ffmpeg` and `ffprobe` are in your `$PATH`.  

---

### 3. Create a virtual environment  
It’s recommended to create a fresh environment:  

```bash
conda create -n audio_env python=3.11
conda activate audio_env
```

Or with `venv`:  

```bash
python -m venv audio_env
source audio_env/bin/activate   # Linux/Mac
audio_env\Scripts\activate      # Windows
```

---

### 4. Install dependencies  
Only new packages are listed in `requirements.txt`.  

```bash
pip install -r requirements.txt
```
Or  
All required packages are listed in `requirements_env.txt`.  

```bash
pip install -r requirements_env.txt
```

---

### 5. Run the Flask app  
Start the server with:  

```bash
python app.py
```

This will:  
- Launch a local web server (`http://127.0.0.1:5000`).  
- Open your browser automatically with the UI.  
- Let you paste a YouTube link, process the song, and download the **8D audio file**.  

---

## 🎛 Testing the Effect  

You can also run a small test script to **visualize** the stereo channels and confirm that the panning effect is applied.  

```bash
python test_audio.py
```

This will display a plot of the left and right channels for the processed audio (`out/effectz.wav`).  
You should see the channels oscillating — meaning the sound will move between left and right in headphones.  

---

## 📂 Project Structure  

- `app.py` → Flask app entry point.  
- `audio_features.py` → Audio DSP methods (panning, normalization, effects).  
- `config.py` → Path to FFmpeg and yt-dlp options.  
- `templates/` → HTML templates for the web app.  
- `static/` → CSS/JS frontend files.  
- `out/` → Temporary folder for processed audio files.  
- `test_audio.py` → Debug tool to visualize stereo channels.  

---

## 📝 Notes  

- **Best experience**: Use headphones (preferably good quality). Laptop speakers or some audio drivers may not clearly reproduce the 8D effect.  
- Some Bluetooth devices may add latency or downmix stereo, making the effect less noticeable.  
- Works with Python **3.11+**.  
