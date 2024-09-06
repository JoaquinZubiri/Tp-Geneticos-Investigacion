import mplfinance as mpl
import matplotlib.pyplot as plt

def velas(df, asset):
    mpl.plot(df, type='candle', volume=False, mav=7, title="Gráfico de Velas - " + asset)

#GRAFICAS COMPARATIVAS PARA VER COMPOSICION FRACTAL
def comparativaFractal(data_1m, data_5m, data_15m):
    plt.figure(figsize=(12, 9))

    plt.subplot(3, 1, 1)
    plt.plot(data_1m["Close"], label="1 minutos")
    plt.title("BTCUSDT - Intervalo de 1 minuto")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(data_5m["Close"], label="5 min")
    plt.title("BTCUSDT - Intervalo de 5 min")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(data_15m["Close"], label="15 min")
    plt.title("BTCUSDT - Intervalo de 15 min")
    plt.legend()

    plt.tight_layout()
    plt.show()

def comparativaCorridas(resultante, base ,coleccion_arrays, original, asset, horaInicioprincipal, horaIniciopredict, horaspredict, tiempo_referencia, long):
    plt.figure(figsize=(12, 7))
    plt.plot(base[:long+1], color='blue') #Close
    for arr in coleccion_arrays:
        plt.plot(range(long, len(arr)), arr[long:])
    plt.legend()

    plt.plot(range(long, long + len(original)), original, label="Close original", color='blue')
    plt.plot(range(long, long + len(original)), resultante, label="RESULTANTE", color='red')
    plt.suptitle('Prediccion de ' + asset)
    horaestudio = horaIniciopredict - horaInicioprincipal # ESTO NO ES EFICIENTE. SIRVE PARA 1 DIA NOMAS. SE PODRIAN PARAMETRIZAR LOS DIAS Y AHI SERIA, O BORRARLO A LA MIERDA. VER SI PODEMOS HACERLO PARA CUALQUIER FECHA.
    if horaIniciopredict - horaInicioprincipal == 0:
        horaestudio = 24

    plt.title("Tiempo de estudio: " + str(horaestudio) + "hs. Tiempo de prediccion: " + str(horaspredict) + "hs. Tamaño de velas: " + str(tiempo_referencia) + "min")
    plt.axvline(x=long, color='green')
    plt.show()