import pandas as pd
import requests
import time

def format_location(city, state):
    return f"{city}, {state}, Brazil"

def get_coords(place):
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "ExcelKMApp/1.0 (moreira.joao.business@gmail.com)"}
    params = {"q": place, "format": "json", "limit": 1}
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            return float(data[0]['lon']), float(data[0]['lat'])
        else:
            return None, None
    except (requests.exceptions.RequestException, ValueError):
        return None, None

def get_distance_osrm(origem, destino):
    lon1, lat1 = get_coords(origem)
    lon2, lat2 = get_coords(destino)

    if None in [lon1, lat1, lon2, lat2]:
        return None

    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        resp = requests.get(osrm_url, timeout=10).json()
        distance_m = resp['routes'][0]['distance']
        return round(distance_m / 1000, 1)
    except (requests.exceptions.RequestException, KeyError, IndexError, ValueError):
        return None

# Ler Excel
df = pd.read_excel("percursos.xlsx")

# Preencher KM
for index, row in df.iterrows():
    if pd.isna(row['KM']):
        origem = format_location(row['CIDADE ORIGEM'], row['UF ORIGEM'])
        destino = format_location(row['CIDADE DESTINO'], row['UF DESTINO'])
        km = get_distance_osrm(origem, destino)
        df.at[index, 'KM'] = km
        print(f"{origem} -> {destino}: {km} km")
        time.sleep(1)

# Salvar resultado
df.to_excel("percursos_com_km.xlsx", index=False)
print("Arquivo salvo!")
