import yfinance as yf 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz

def analizar_activo(symbol, nombre):
    print(f"\nDescargando datos para {nombre} ({symbol})...")
    data = yf.download(tickers=symbol, interval="5m", period="5d")
    data = data.dropna()

    data['log_return'] = np.log(data['Close'] / data['Close'].shift(1))
    window = 20
    threshold = 2

    data['mean'] = data['log_return'].rolling(window=window).mean()
    data['std'] = data['log_return'].rolling(window=window).std()

    data['upper'] = data['mean'] + threshold * data['std']
    data['lower'] = data['mean'] - threshold * data['std']

    data['anomaly'] = (data['log_return'] > data['upper']) | (data['log_return'] < data['lower'])

    if data['anomaly'].any():
        anomalies = data[data['anomaly']].copy()
        last_5_anomalies = anomalies.tail(5)

        print("\nÚltimas 5 anomalías detectadas (hora NY):")
        for idx, row in last_5_anomalies.iterrows():
            if idx.tzinfo is None:
                idx = idx.tz_localize('UTC')
            idx_ny = idx.tz_convert('America/New_York')
            log_return_val = float(row['log_return'])
            print(f"- {idx_ny.strftime('%Y-%m-%d %H:%M:%S')} | Log Return: {log_return_val:.5f}")

        last_anomaly = last_5_anomalies.iloc[-1]
        last_anomaly_time_utc = last_5_anomalies.index[-1]
        if last_anomaly_time_utc.tzinfo is None:
            last_anomaly_time_utc = last_anomaly_time_utc.tz_localize('UTC')
    else:
        print("\nNo se detectaron anomalías.")
        last_anomaly = None

    plt.figure(figsize=(15,6))
    plt.plot(data.index, data['log_return'], label='Log Return', color='black', alpha=0.5)
    plt.plot(data.index, data['upper'], label='Upper Threshold', color='red', linestyle='--')
    plt.plot(data.index, data['lower'], label='Lower Threshold', color='green', linestyle='--')
    plt.scatter(data[data['anomaly']].index, data[data['anomaly']]['log_return'], color='orange', label='Anomalies', zorder=5)

    if last_anomaly is not None:
        log_ret = float(last_anomaly['log_return'])
        upper = float(last_anomaly['upper'])
        direction = "por arriba" if log_ret > upper else "por debajo"
        plt.annotate(
            f"Rendimiento logarítmico {direction} de 2 desviaciones estándar\nBuscar posible corrección",
            xy=(last_anomaly_time_utc, log_ret),
            xytext=(last_anomaly_time_utc, log_ret + 0.002),
            arrowprops=dict(facecolor='red', shrink=0.05),
            fontsize=9,
            backgroundcolor='yellow'
        )

    plt.title(f'Anomalías en los Rendimientos Logarítmicos - {nombre} ({symbol})')
    plt.xlabel('Fecha')
    plt.ylabel('Log Return')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def menu():
    intro_text = """
    *** Indicador Estadístico de Anomalías en Rendimientos Logarítmicos ***

    Este programa no es una estrategia de trading, sino un indicador que mide
    condiciones estadísticas del mercado mediante el análisis de los rendimientos
    logarítmicos intradía del activo seleccionado.

    IMPORTANTE:
    - No tomar decisiones solo con este indicador.
    - Complementar con AMT, contexto y análisis técnico.

    """

    print(intro_text)

    while True:
        print("\nSeleccione un activo para analizar:")
        print("1. S&P 500 (^GSPC)")
        print("2. NASDAQ 100 (^NDX)")
        print("3. EURJPY (EURJPY=X)")
        print("4. Salir")

        opcion = input("Ingrese opción (1-4): ").strip()

        if opcion == '1':
            analizar_activo("^GSPC", "S&P 500")
        elif opcion == '2':
            analizar_activo("^NDX", "NASDAQ 100")
        elif opcion == '3':
            analizar_activo("EURJPY=X", "EURJPY")
        elif opcion == '4':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    menu()
