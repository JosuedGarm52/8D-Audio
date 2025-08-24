import logging
from flask import Flask, render_template, Response, request, send_file, jsonify
from pathlib import Path
import json
import traceback

# Intentar importar dependencias críticas
MISSING_DEPENDENCIES = []
try:
    from audio_features import song_features, download_from_youtube, rotate_left_right, save_song, add_effects
except ImportError as e:
    MISSING_DEPENDENCIES.append(str(e))

# Configuración de logging
LOG_FILE = "app.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
APP_ROOT = Path(__file__).parent


# Limpiar archivos previos
def clear_directories():
    for file_name in ['out/test.wav', 'out/effectz.wav', 'out/in.wav']:
        file_path = APP_ROOT / file_name
        try:
            file_path.unlink(missing_ok=True)
            logging.info(f"Eliminado: {file_path}")
        except Exception as e:
            logging.error(f"No se pudo eliminar {file_path}: {e}")
    return "Done Path Clearing"


# Página principal
@app.route('/')
def index():
    if MISSING_DEPENDENCIES:
        msg = f"⚠️ Dependencias faltantes: {MISSING_DEPENDENCIES}"
        logging.error(msg)
        return msg
    return render_template('index.html')


# Descargar archivo procesado
@app.route('/out/effectz.wav')
def download_file():
    file_path = APP_ROOT / 'out/effectz.wav'
    if file_path.exists():
        return send_file(file_path)
    logging.warning("Intento de descarga pero no existe effectz.wav")
    return "Archivo no encontrado"


# Convertir audio desde YouTube
@app.route('/convert', methods=['POST'])
def convert():
    url = request.values.get('url')

    def process_audio(url):
        logs = []
        try:
            logs.append("Limpiando directorios...")
            clear_directories()

            logs.append("Descargando audio...")
            wav_file = download_from_youtube(url)

            logs.append("Procesando audio...")
            wav_mono, wav_stereo, sampling_rate, tempo, beat_frame = song_features(wav_file)

            logs.append("Aplicando efecto 8D...")
            wav = rotate_left_right(wav_mono, wav_stereo, tempo, sampling_rate)

            logs.append("Guardando audio...")
            save_song('./out/in.wav', wav, sampling_rate)

            logs.append("Añadiendo efectos...")
            add_effects('./out/in.wav')

            logs.append("¡Listo!")

            yield json.dumps({"success": True, "logs": logs})

        except Exception as e:
            # Log completo para consola
            print(traceback.format_exc())
            # Enviar solo el mensaje resumido al cliente
            yield json.dumps({"success": False, "error": str(e)})

    return Response(process_audio(url), mimetype='text/plain')


if __name__ == '__main__':
    try:
        logging.info("Iniciando servidor Flask...")
        app.run(debug=True)
    except Exception as e:
        logging.exception("Error crítico al iniciar Flask")
