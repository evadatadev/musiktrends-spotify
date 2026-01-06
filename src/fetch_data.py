import os
import requests
from datetime import datetime, timedelta

# Daten speichern in data/raw 
RAW_DATA_PATH = "data/raw/spotify-weekly"
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# Zeitraum definieren
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

current = start_date

# Log
print(f"Starte Download-Prozess in den Ordner: {RAW_DATA_PATH}")

# Automatisierter Download mit einer Schleife
while current < end_date:
    # Daten formatieren (YYYY-MM-DD)
    week_start = current.strftime("%Y-%m-%d")
    # Ende der Woche berechnen
    week_end = (current + timedelta(days=7)).strftime("%Y-%m-%d")

    # URL der Spotify Charts
    url = f"https://spotifycharts.com/regional/global/weekly/{week_start}--{week_end}/download"

    # Dateiname mit dem neuen Pfad-Präfix
    filename = os.path.join(RAW_DATA_PATH, f"spotify_global_weekly_{week_start}_{week_end}.csv")

    # Log
    print(f"Versuche: {week_start} bis {week_end} ...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)

        # Prüfen, ob der Download erfolgreich war (HTTP Status: 200)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print("Erfolgreich gespeichert.")
        else:
            # Falls Daten nicht bereit bestehen, gibt Spotify oft 404 zurück
            print(f"Nicht verfügbar (Status: {response.status_code})")

    except requests.exceptions.RequestException as e:
        print(f"Netzwerkfehler: {e}")

    # 7 Tage weiter springen zur nächsten Woche
    current += timedelta(days=7)

# Log
print("\nDownload-Vorgang abgeschlossen.")
    
                        