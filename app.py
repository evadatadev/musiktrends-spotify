import os
import re
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

import streamlit as st
import plotly.express as px

from src.spotify_client import SpotifyClient, extract_track_id
from src.predict_pipeline import run_prediction_pipeline
from src.features import build_features, generate_trend_report

# ------------------------------------------------------------
# Seiteneinstellungen
# ------------------------------------------------------------
st.set_page_config(
    page_title="Spotify Rising Artist Predictor",
    page_icon="🎵",
    layout="wide"
)

# ------------------------------------------------------------
# Modell-Check
# ------------------------------------------------------------
MODEL_FILES = {
    "Prophet": "models/market_trend_prophet_v1.json",
    "LightGBM": "models/rising_artist_lgbm_v1.txt",
    "Threshold": "models/rising_artist_threshold.json",
    "Feature Columns": "models/rising_artist_features.json"
}

def check_models():
    missing = [name for name, path in MODEL_FILES.items() if not os.path.exists(path)]
    return missing

missing_models = check_models()

# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def extract_date_from_filename(filename: str):
    """Extrahiert ein Datum im Format YYYY-MM-DD aus dem Dateinamen."""
    match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
    if match:
        return pd.to_datetime(match.group(0), errors="coerce")
    return pd.NaT

# ------------------------------------------------------------
# Spotify Client (einmalig erstellen)
# ------------------------------------------------------------
@st.cache_resource
def get_spotify_client():
    return SpotifyClient()

# ------------------------------------------------------------
# Caching-Helfer
# ------------------------------------------------------------
@st.cache_data(show_spinner="Verwende Cache für Track-IDs...")
def cached_get_ids(df_new: pd.DataFrame):
    client = get_spotify_client()
    return client.get_ids_for_tracks(df_new)

@st.cache_data(show_spinner="Verwende Cache für Spotify-Metadaten...")
def cached_enrich_data(df_with_ids: pd.DataFrame):
    client = get_spotify_client()
    return client.enrich_data(df_with_ids)

@st.cache_data(show_spinner="Verwende Cache für Modellvorhersagen...")
def cached_run_prediction(df_features: pd.DataFrame):
    preds, probs = run_prediction_pipeline(df_features)
    df_out = df_features.copy()
    df_out["is_rising"] = preds
    df_out["probability"] = probs
    return df_out

# ------------------------------------------------------------
# UI Header
# ------------------------------------------------------------
st.title("🎵 Musiktrends: Rising Artist Radar")

st.markdown("""
Dieses Dashboard nutzt **Prophet** für Makro-Trends und **LightGBM** zur Identifizierung 
von Newcomern mit hohem Aufstiegspotenzial.
""")

# Sidebar
st.sidebar.header("Systemstatus")
if missing_models:
    st.sidebar.error("Fehlende Modelle:")
    for m in missing_models:
        st.sidebar.write(f"• {m}")
else:
    st.sidebar.success("Alle Modelle erfolgreich geladen.")

st.sidebar.markdown("---")
st.sidebar.markdown("**Hinweis:** API-Calls und Modellvorhersagen werden gecached, um die Performance zu verbessern.")

# ------------------------------------------------------------
# Datei-Upload
# ------------------------------------------------------------
st.subheader("1. Neue Chart-Daten hochladen")
uploaded_file = st.file_uploader(
    "Wähle die aktuelle Spotify-Charts CSV (Download von charts.spotify.com)",
    type="csv"
)

if uploaded_file is None:
    st.info("Bitte lade eine CSV-Datei hoch, um die Analyse zu starten.")
    st.stop()

# CSV laden
df_new = pd.read_csv(uploaded_file)

# chart_week aus Dateiname ableiten
chart_week = extract_date_from_filename(uploaded_file.name)
df_new["chart_week"] = chart_week

# track_id aus uri extrahieren
if "uri" in df_new.columns:
    df_new["track_id"] = df_new["uri"].apply(extract_track_id)

st.write(f"Vorschau der hochgeladenen Daten ({len(df_new)} Zeilen):")
st.dataframe(df_new.head())

# ------------------------------------------------------------
# Analyse starten
# ------------------------------------------------------------
if st.button("🚀 Analyse starten"):
    with st.spinner("Verbinde mit Spotify API und berechne Vorhersagen..."):
        try:
            # 1. IDs + Metadaten
            st.text("Hole Spotify-IDs...")
            df_with_ids = cached_get_ids(df_new)

            st.text("Hole Spotify-Metadaten (Genres, Popularity, etc.)...")
            df_enriched = cached_enrich_data(df_with_ids)

            st.text("Berechne Feature-Engineering...")
            df_features = build_features(df_enriched)

            # Prophet benötigt 'ds'
            df_features["ds"] = pd.to_datetime(df_features["chart_week"], errors="coerce")

            # 2. Modell-Vorhersagen
            st.text("KI-Modelle berechnen Wahrscheinlichkeiten...")
            df_final = cached_run_prediction(df_features)

            st.success("Analyse abgeschlossen!")

            # --------------------------------------------------------
            # Neue Daten an Historie anhängen
            # --------------------------------------------------------
            
            # --------------------------------------------------------
            # Option: Neue Daten an Historie anhängen (nur Metadaten!)
            # --------------------------------------------------------
            st.markdown("### 📦 Datenverwaltung")

            if st.checkbox("Neue Woche an historische Daten anhängen"):
                try:
                    HIST_PATH = "data/processed/final_data_with_metadata.csv"

                    # Historische Datei laden oder neu erstellen
                    if os.path.exists(HIST_PATH):
                        df_hist = pd.read_csv(HIST_PATH)
                    else:
                        st.warning("Historische Datei existiert nicht – sie wird neu erstellt.")
                        df_hist = pd.DataFrame()
            
                    # ❗ Nur Metadaten speichern – keine Features, keine Predictions
                    allowed_cols = [
                        "chart_week",
                        "rank",
                        "artist_names",
                        "track_name",
                        "peak_rank",
                        "previous_rank",
                        "weeks_on_chart",
                        "streams",
                        "track_id",
                        "artist_id",
                        "release_date",
                        "explicit",
                        "track_popularity",
                        "artist_genres",
                        "artist_followers",
                        "artist_popularity"
                    ]
            
                    # Nur die erlaubten Spalten übernehmen
                    df_to_append = df_enriched.copy()
                    df_to_append = df_to_append[[col for col in allowed_cols if col in df_to_append.columns]]
            
                    # Historie + neue Daten kombinieren
                    df_updated = pd.concat([df_hist, df_to_append], ignore_index=True)
            
                    # Dubletten entfernen (Track + Woche)
                    df_updated = df_updated.drop_duplicates(
                        subset=["track_id", "chart_week"], keep="last"
                    )
            
                    # Speichern
                    df_updated.to_csv(HIST_PATH, index=False)
            
                    st.success(f"Neue Woche erfolgreich gespeichert unter:\n**{HIST_PATH}**")
            
                except Exception as e:
                    st.error(f"Fehler beim Aktualisieren der historischen Daten: {e}")

            # --------------------------------------------------------
            # Dashboard-Bereich
            # --------------------------------------------------------
            st.subheader("2. Ergebnisse & Visualisierungen")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Anzahl Tracks", len(df_final))
            with col2:
                st.metric("Identifizierte Rising Artists", int(df_final["is_rising"].sum()))
            with col3:
                st.metric(
                    "Max. Rising-Wahrscheinlichkeit",
                    f"{df_final['probability'].max():.2f}" if len(df_final) > 0 else "–"
                )

            # Top 10
            top_10 = (
                df_final[df_final["is_rising"] == 1]
                .sort_values("probability", ascending=False)
                .head(10)
            )

            if top_10.empty:
                st.warning("Keine Rising Artists mit positiver Vorhersage gefunden.")
            else:
                st.markdown("### Top 10 Potenzielle Aufsteiger")
                st.dataframe(top_10[["track_name", "artist_names", "probability"]])

                fig = px.bar(
                    top_10,
                    x="probability",
                    y="track_name",
                    color="artist_names",
                    orientation="h",
                    title="Top 10 Rising Artists – Modellwahrscheinlichkeiten",
                    labels={
                        "probability": "Wahrscheinlichkeit",
                        "track_name": "Track",
                        "artist_names": "Artist"
                    }
                )
                fig.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Trendberichte
                st.markdown("### 📈 Trendberichte – Warum sind diese Artists Rising?")
                for _, row in top_10.iterrows():
                    report = generate_trend_report(row)
                    st.markdown(report)
                    st.markdown("---")

        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")