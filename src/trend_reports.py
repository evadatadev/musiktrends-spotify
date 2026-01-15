import os
import pandas as pd
from google import genai

def generate_gemini_report(df_display, top_10):
    """
    Erstellt einen KI-Trendbericht basierend auf den aktuellen Dashboard-Daten.
    """
    # API-Key laden
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Fehler: Kein Google API Key in der .env gefunden."
        
    client = genai.Client(api_key=api_key)

    # Datencheck
    if df_display.empty:
        return "Keine Daten verfügbar, um einen Bericht zu erstellen."

    if top_10.empty:
        return "Top-10-Daten fehlen. Ein Bericht kann nicht erstellt werden."
    
    # Daten-Aggregation für den Prompt
    if "artist_genres" in df_display.columns:
        df_genres = df_display.copy()
        df_genres["artist_genres"] = df_genres["artist_genres"].apply(
            lambda x: x if isinstance(x, list) else [str(x)] if pd.notna(x) else ["unknown"]
        )
        df_genres = df_genres.explode("artist_genres")
        top_genres = (
            df_genres["artist_genres"]
            .value_counts()
            .head(5)
            .index
            .tolist()
        )
    else:
        top_genres = ["unknown"]
        
    # Top-Song & Artist
    top_artist = top_10.iloc[0].get("artist_names", "Unbekannter Artist")
    top_song = top_10.iloc[0].get("track_name", "Unbekannter Song")

    # Rising Artists
    rising_count = (
        df_display["probability"] >= 0.9
    ).sum() if "probability" in df_display.columns else 0
        

    prompt = f"""
    Du bist ein professioneller Musik-Datenanalyst für Spotify Trends.
    
    Erstelle eine Prognose für die kommende Woche. 
    WICHTIG: Die folgenden Werte stammen aus einem KI-Vorhersagemodell und beziehen sich NICHT auf die aktuelle Woche, 
    sondern auf die erwartete Entwicklung der nächsten Woche. 
    Verwende ausschließlich die bereitgestellten Daten und erfinde keine zusätzlichen Genres, Künstler, Songs oder Zahlen.
    
    Nutze die Modell-Ergebnisse, um einzuschätzen, welche Artists in der nächsten Woche besonders stark an Momentum gewinnen werden:
    
    🎧 Prognostisch relevante Genres: {', '.join(top_genres)}
    ⭐ Höchstbewerteter Artist laut Modell: {top_artist} – Song: '{top_song}'
    📈 Anzahl prognostizierter Rising Artists (>90% Wahrscheinlichkeit): {rising_count}
    📊 Datenbasis der Modellberechnung: {len(df_display)} Tracks
    
    Schreibe einen kurzen, prägnanten Bericht auf Deutsch.
    Verwende Emojis, klare Bulletpoints und formuliere wie ein echter Musik-Analyst.
    """

    # Anfrage an Gemini 2.5 Flash
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return response.text or "Fehler: Leere Antwort von Gemini."
    except Exception as e:
        return f"KI-Fehler: {str(e)}"
