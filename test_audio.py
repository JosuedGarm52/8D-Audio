import matplotlib.pyplot as plt
import torchaudio
import os

def test_plot_effects(file_path="out/effectz.wav", n_samples=2000):
    """
    Grafica los primeros n_samples del archivo de salida para comprobar
    diferencias entre canal izquierdo y derecho.
    Maneja errores si el archivo no existe o no se puede leer.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        wav, sr = torchaudio.load(file_path)  # wav shape = [channels, samples]

        plt.figure(figsize=(10, 4))
        plt.plot(wav[0][:n_samples], label="Canal Izquierdo")
        plt.plot(wav[1][:n_samples], label="Canal Derecho")
        plt.title("Comparación de canales (ejemplo de paneo)")
        plt.legend()
        plt.show()

    except FileNotFoundError as e:
        print(f"[Error] {e}")
    except RuntimeError as e:
        print(f"[Error] Could not read audio file: {e}")
    except Exception as e:
        print(f"[Unexpected error] {e}")

if __name__ == "__main__":
    try:
        test_plot_effects()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
