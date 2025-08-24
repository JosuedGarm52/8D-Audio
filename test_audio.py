import matplotlib.pyplot as plt
import torchaudio

def test_plot_effects(file_path="out/effectz.wav", n_samples=2000):
    """
    Grafica los primeros n_samples del archivo de salida para comprobar
    diferencias entre canal izquierdo y derecho.
    """
    wav, sr = torchaudio.load(file_path)  # wav shape = [channels, samples]

    plt.figure(figsize=(10, 4))
    plt.plot(wav[0][:n_samples], label="Canal Izquierdo")
    plt.plot(wav[1][:n_samples], label="Canal Derecho")
    plt.title("Comparación de canales (ejemplo de paneo)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    test_plot_effects()
