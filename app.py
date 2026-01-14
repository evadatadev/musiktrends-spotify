import os
import pandas as pd
import streamlit as st
import plotly.express as px

from src.extraction_unique_entities import prepare_unique_tracks
from src.spotify_client import SpotifyClient
from src.merge_dataframes import merge_new_data
from src.features import build_features, generate_trend_report
from src.predict_pipeline import run_prediction_pipeline


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
# UI Header
# ------------------------------------------------------------
st.title("🎵 Musiktrends: Rising Artist Radar")

st.markdown("""
Entdecken Sie, welche Künstler gerade an Fahrt aufnehmen. Unsere KI analysiert aktuelle Chartdaten und erkennt frühzeitig, welche Newcomer das Potenzial haben, ganz groß zu werden.
""")

# Sidebar
st.sidebar.header("🔧 Systemstatus")
if missing_models:
    st.sidebar.error("Modelle konnten nicht geladen werden:")
    for m in missing_models:
        st.sidebar.write(f"• {m}")
else:
    st.sidebar.success("System bereit!")
    st.sidebar.caption("Alle Modelle geladen.")

# ------------------------------------------------------------
# Datei-Upload 
# ------------------------------------------------------------
st.header("📁 Neue Chart-Daten hochladen")
uploaded_file = st.file_uploader(
    "Wähle die aktuelle Spotify-Charts CSV (Download von charts.spotify.com)",
    type="csv"
)

if uploaded_file is None:
    st.info("Bitte lade eine CSV-Datei hoch, um die Analyse zu starten.")
    st.stop()

# ------------------------------------------------------------ 
# Datei speichern 
# ------------------------------------------------------------
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

temp_path = f"{RAW_DIR}/{uploaded_file.name}"

with open(temp_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

st.success(f"Datei wurde erfolgreich hochgeladen.")
st.caption(f"Speicherort: {temp_path}")

# ------------------------------------------------------------ 
# Schritt 1: Unique Tracks extrahieren 
# ------------------------------------------------------------
st.subheader("🔍 Titel & Künstler automatisch erkennen")

unique_path, date_str = prepare_unique_tracks(temp_path)

st.success(f"Titel und Künstler wurden erkannt und gespeichert.")
st.caption(f"Speicherort: {unique_path}")

# ---------------------------------------------------------------- 
# Schritt 2: Spotify Enrichment Pipeline mit anschließendem Merge 
# ----------------------------------------------------------------
st.subheader("🎼 Spotify-Daten erweitern")

if st.button("🎧 Spotify-Infos laden"):
    with st.spinner("Hole Spotify-IDs und Metadaten..."):
        client = SpotifyClient()

        df_enriched = client.run_full_pipeline(
            unique_tracks_csv=unique_path,
            date_str=date_str,
            output_dir="data/interim"
        )
    st.success("Die Titel wurden erfolgreich mit Spotify-Infos angereichert.")

    df_final = merge_new_data(
        ids_csv=f"data/interim/unique_tracks_with_ids_{date_str}.csv",
        enriched_csv=f"data/interim/enriched_data_{date_str}.csv",
        hist_path="data/processed/final_data_with_metadata.csv",
        output_path=f"data/interim/merged_enriched_{date_str}.csv",
        backup_dir="data/backups",
        cleanup_days=180
    )

    st.success("Die neuen Daten wurden erfolgreich mit der Historie verbunden.")
    
    st.write("Vorschau der angereicherten Daten:")
    st.dataframe(df_final.head())
    
    # -------------------------------------------------------- 
    # Schritt 3: Feature Engineering 
    # -------------------------------------------------------- 
    st.header("🧠 2. Daten verarbeiten")
    st.subheader("🧩 Merkmale berechnen") 
    
    df_features = build_features(df_final) 
    df_features["ds"] = pd.to_datetime(df_features["chart_week"], errors="coerce") 
    
    st.success("Die Daten wurden erfolgreich aufbereitet.")

    # -------------------------------------------------------- 
    # Schritt 4: Prediction Pipeline 
    # -------------------------------------------------------- 
    st.subheader("🤖 KI‑Vorhersage starten") 
    
    preds, probs = run_prediction_pipeline(df_features) 
    
    df_features["is_rising"] = preds 
    df_features["probability"] = probs 
    
    st.success("Die KI-Vorhersagen sind bereit.")

    # -------------------------------------------------------- 
    # Schritt 5: TOP‑10 Rising Artists 
    # -------------------------------------------------------- 
    st.header("📊 3. Ergebnisse entdecken")
    st.subheader("🚀 Vorhergesagte TOP 10 aufstrebende Künstler der nächsten Woche") 
    
    df_top10 = df_features.sort_values("probability", ascending=False).head(10) 
    
    st.dataframe(df_top10[[ 
        "artist_names", "track_name", "probability", 
        "track_popularity", "artist_followers", "genre_pop_idx" 
    ]])

    # -------------------------------------------------------- 
    # Dashboard-Bereich 
    # -------------------------------------------------------- 
    st.subheader("📊 Überblick & Entwicklungen") 
    
    col1, col2, col3 = st.columns(3) 
    with col1: 
        st.metric("Anzahl Tracks", len(df_features)) 
    with col2: 
        st.metric("Identifizierte Rising Artists", int(df_features["is_rising"].sum())) 
    with col3: 
        st.metric( 
            "Max. Rising-Wahrscheinlichkeit", 
            f"{df_features['probability'].max():.2f}" if len(df_features) > 0 else "–" 
        ) 
    # Plot: Top 10 Rising Artists 
    if df_top10.empty: 
        st.warning("Keine Rising Artists mit positiver Vorhersage gefunden.") 
    else: 
        st.markdown("### 🎤 Top 10 – Modellwahrscheinlichkeiten") 
        
        fig = px.bar( 
            df_top10, 
            x="probability", 
            y="track_name", 
            color="artist_names", 
            orientation="h", 
            title="Top 10 Rising Artists (Modellwahrscheinlichkeiten)", 
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

    # -------------------------------------------------------- 
    # Schritt 6: Trendbericht
    # -------------------------------------------------------- 
    st.subheader("📝 Trendbericht") 
    
    for _, row in df_top10.iterrows(): 
        report = generate_trend_report(row) 
        st.markdown(report) 
        st.markdown("---") 