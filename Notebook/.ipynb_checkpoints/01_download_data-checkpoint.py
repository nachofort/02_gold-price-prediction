import yfinance as yf
import pandas as pd
import time
import os  

# Diccionario con 19 variables 
tickers_proyecto = {
    "Precio_Oro": "GC=F",          
    "Indice_Dolar_DXY": "UUP",     
    "Cambio_EUR_USD": "EURUSD=X",  
    "Cambio_USD_JPY": "JPY=X",     
    "Cambio_USD_CNY": "CNY=X",     
    "Bolsa_SP500": "^GSPC",        
    "Bolsa_NASDAQ": "^NDX",        
    "Volatilidad_VIX": "^VIX",     
    "Bolsa_MSCI_World": "URTH",    
    "Bono_EEUU_10Y": "^TNX",       
    "Bono_EEUU_3M": "^IRX",     
    "Petroleo_Brent": "BZ=F",      
    "Precio_Plata": "SI=F",        
    "Precio_Cobre": "HG=F",        
    "Precio_Trigo": "ZW=F",        
    "Mineras_Oro_GDX": "GDX",      
    "Bitcoin_USD": "BTC-USD",      
    "Bonos_Corporativos_LQD": "LQD",
    "ETF_Oro_Fisico_GLD": "GLD"    
}

FECHA_INICIO = "2019-01-01"
FECHA_FIN = "2026-06-01"

print("🚀 Iniciando la descarga masiva mediante método Ticker.history (Blindado)...")
dataframes_individuales = []

# 2. Bucle de descarga selectiva (solo precios de cierre)
for nombre_variable, codigo_ticker in tickers_proyecto.items():
    try:
        print(f"Descargando {nombre_variable} [{codigo_ticker}]...")
        
        activo = yf.Ticker(codigo_ticker)
        ticket_descarga = activo.history(start=FECHA_INICIO, end=FECHA_FIN)
        
        if ticket_descarga.empty:
            print(f"⚠️ {nombre_variable} no devolvió datos. Saltando...")
            continue

        # Normalización temporal: Eliminamos zona horaria y forzamos hora a 00:00:00
        ticket_descarga.index = ticket_descarga.index.tz_localize(None).normalize()
        
        # Agrupación de seguridad por si hay duplicados intrasemanales
        ticket_descarga = ticket_descarga.groupby(ticket_descarga.index).last()
        
        # Extraemos únicamente el precio de cierre limpio
        precio_cierre = ticket_descarga['Close']
        df_limpio = precio_cierre.to_frame(name=nombre_variable)
        dataframes_individuales.append(df_limpio)
        
        # Pausa de cortesía para evitar bloqueos de la API (Rate Limiting)
        time.sleep(0.3)
        
    except Exception as e:
        print(f"❌ Error al descargar {nombre_variable}: {e}")

#  Combinación y sincronización de las series temporales
if len(dataframes_individuales) == 0:
    print("❌ Error crítico: No se pudo construir ningún DataFrame. Revisa tu conexión.")
else:
    print("\nEnlazando todas las variables mediante su serie temporal común...")
    dataset_final = pd.concat(dataframes_individuales, axis=1)
    
    # Saneamiento secuencial: Relleno hacia adelante y eliminación de remanentes iniciales
    dataset_final = dataset_final.ffill().dropna()
    
    try:
        ruta_origen = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        ruta_origen = os.getcwd()

    carpeta_datos = os.path.normpath(os.path.join(ruta_origen, "..", "Data"))
    nombre_archivo = os.path.join(carpeta_datos, "dataset_analisis_oro.csv")
    
    if not os.path.exists(carpeta_datos):
        os.makedirs(carpeta_datos)
        print(f"📁 La carpeta '{carpeta_datos}' no existía, creada automáticamente.")
   
    dataset_final.to_csv(nombre_archivo)
    
    print("-" * 60)
    print(f"🎯 ¡CONSEGUIDO! Tu laboratorio de datos ha quedado impecable.")
    print(f"Archivo guardado en: '{nombre_archivo}'")
    print(f"Dimensiones finales: {dataset_final.shape[0]} filas (días) x {dataset_final.shape[1]} columnas.")
    print("-" * 60)
    
    print(dataset_final.head())