import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
import torchaudio
from yt_dlp import YoutubeDL
from scipy.signal import butter, lfilter
from config import YDL_OPTIONS
import os
import logging

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
    """Paneo continuo para efecto 8D simple."""
    length = wav_mono.shape[0]
    t = np.arange(length) / sr  # tiempo en segundos

    # Frecuencia de oscilación en Hz (ajústala según el ritmo deseado)
    f = tempo / 60 / 8  # un ciclo cada 1/8 de compás aprox

    # Generar señal de paneo: varía entre 0 (izq) y 1 (der)
    pan = 0.5 * (1 + np.sin(2 * np.pi * f * t))

    # Aplicar al audio
    wav_stereo[0, :] = wav_mono * (1 - pan)  # canal izquierdo
    wav_stereo[1, :] = wav_mono * pan      # canal derecho

    return wav_stereo

def add_effects(input_path, output_path="out/effectz.wav"):
    # Cargar audio
    waveform, sr = torchaudio.load(input_path)  # [canales, samples]

    # Mantener estéreo y normalizar volumen
    max_val = waveform.abs().max()
    if max_val > 0:
        waveform = waveform / max_val  # normalización

    # Ejemplo opcional: añadir un pequeño reverb "simulado"
    # solo mezcla ligera entre canales para reforzar efecto 3D
    if waveform.shape[0] == 2:  # stereo
        left, right = waveform
        mix = 0.02  # mezcla mínima de un canal al otro
        waveform[0] = left * (1 - mix) + right * mix
        waveform[1] = right * (1 - mix) + left * mix

    # Crear carpeta si no existe
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardar audio final
    torchaudio.save(str(output_path), waveform, sr)
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
