import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
import sox
from yt_dlp import YoutubeDL
from scipy.signal import butter, lfilter
from config import YDL_OPTIONS
import os

APP_ROOT = Path(__file__).parent
OUT_DIR = APP_ROOT / "out"
OUT_DIR.mkdir(exist_ok=True)

# ===========================
# Funciones de audio
# ===========================

def song_features(file_name, duration=270):
    """Carga archivo WAV y devuelve mono, stereo, sampling rate, tempo y beat frames."""
    wav_mono, sr = librosa.load(file_name, duration=duration)
    wav_stereo, sr = librosa.load(file_name, mono=False, duration=duration)
    tempo, beat_frames = librosa.beat.beat_track(y=wav_stereo[0], sr=sr)
    return wav_mono, wav_stereo, sr, tempo, beat_frames

def save_song(file_name, wav, sampling_rate):
    """Guarda la señal de audio en WAV."""
    sf.write(file_name, wav.T if wav.ndim==2 else wav, sampling_rate)

def rotate_left_right(wav_mono, wav_stereo, tempo, sr):
    """Efecto 8D simple, alterna amplitudes en canales izquierdo/derecho."""
    length = wav_mono.shape[0]
    end_of_beat = int((tempo / 120) * sr)
    down_value = 0.15
    amp_down = np.linspace(1, down_value, 2*end_of_beat)
    amp_up = np.linspace(down_value, 1, 2*end_of_beat)
    amp_down_slow = np.linspace(1, down_value, 8*end_of_beat)
    amp_up_slow = np.linspace(down_value, 1, 8*end_of_beat)

    left_up, right_up = False, False
    left_maintain, right_maintain = False, True
    i = 0

    while i < length - 8*end_of_beat:
        fast = np.random.choice([True, False])
        if left_up:
            if fast:
                wav_stereo[0, i:i+2*end_of_beat] = wav_mono[i:i+2*end_of_beat]*amp_up
                wav_stereo[1, i:i+2*end_of_beat] = wav_mono[i:i+2*end_of_beat]*amp_down
                left_up, left_maintain = False, True
                i += 2*end_of_beat
            else:
                wav_stereo[0, i:i+8*end_of_beat] = wav_mono[i:i+8*end_of_beat]*amp_up_slow
                wav_stereo[1, i:i+8*end_of_beat] = wav_mono[i:i+8*end_of_beat]*amp_down_slow
                left_up, left_maintain = False, True
                i += 8*end_of_beat
        elif right_up:
            if fast:
                wav_stereo[1, i:i+2*end_of_beat] = wav_mono[i:i+2*end_of_beat]*amp_up
                wav_stereo[0, i:i+2*end_of_beat] = wav_mono[i:i+2*end_of_beat]*amp_down
                right_up, right_maintain = False, True
                i += 2*end_of_beat
            else:
                wav_stereo[1, i:i+8*end_of_beat] = wav_mono[i:i+8*end_of_beat]*amp_up_slow
                wav_stereo[0, i:i+8*end_of_beat] = wav_mono[i:i+8*end_of_beat]*amp_down_slow
                right_up, right_maintain = False, True
                i += 8*end_of_beat
        elif left_maintain:
            wav_stereo[0, i:i+end_of_beat] = wav_mono[i:i+end_of_beat]
            wav_stereo[1, i:i+end_of_beat] = wav_mono[i:i+end_of_beat]*down_value
            right_up, left_maintain = True, False
            i += end_of_beat
        elif right_maintain:
            wav_stereo[1, i:i+end_of_beat] = wav_mono[i:i+end_of_beat]
            wav_stereo[0, i:i+end_of_beat] = wav_mono[i:i+end_of_beat]*down_value
            right_maintain, left_up = False, True
            i += end_of_beat

    # silenciar final incompleto
    wav_stereo[0, (length//(8*end_of_beat))*(8*end_of_beat):] *= 0
    wav_stereo[1, (length//(8*end_of_beat))*(8*end_of_beat):] *= 0
    return wav_stereo

def add_effects(input_path, output_path="out/effectz.wav"):
    tfm = sox.Transformer()

    # Ejemplo de efectos (puedes ajustar a tu gusto)
    tfm.reverb(reverberance=50, room_scale=50)
    tfm.bass(gain=5)
    tfm.treble(gain=3)

    # Exportar
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tfm.build(str(input_path), str(output_path))
    return str(output_path)

# ===========================
# Filtros y elevación
# ===========================

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    b, a = butter(order, cutoff/nyq, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order)
    return lfilter(b, a, data)

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    b, a = butter(order, cutoff/nyq, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order)
    return lfilter(b, a, data)

def elevation(wav_mono, tempo, sr):
    length = len(wav_mono)
    end_of_beat = int((tempo / 120) * sr) * 2
    y = np.array([], dtype=float)
    order = 6
    fs = 30.0
    i = 1

    while i < length:
        # low-pass
        for cutoff in [10, 9.25, 8.75, 8]:
            y = np.append(y, butter_lowpass_filter(wav_mono[i:i+end_of_beat], cutoff, fs, order))
            i += end_of_beat
        # high-pass
        for cutoff in [8, 8.75, 9.25, 10]:
            y = np.append(y, butter_highpass_filter(wav_mono[i:i+end_of_beat], cutoff, fs, order))
            i += end_of_beat

    return y

# ===========================
# YouTube download
# ===========================
def download_from_youtube(url, output_path="out/test"):
    # Asegurarse de que la carpeta exista
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ydl_opts = {
        **YDL_OPTIONS,
        'outtmpl': output_path,  # Sin extensión
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # El archivo final será output_path + ".wav"
    final_file = output_path + ".wav"
    return final_file
