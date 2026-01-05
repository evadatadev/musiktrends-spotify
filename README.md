# 🎵 Musiknutzungs‑Trends & KI‑basierte Vorhersagen  
**Analyse von Spotify‑Charts, API‑Metadaten, Machine Learning & interaktivem Dashboard**

---

## 📅 Roadmap
- [in Arbeit ...] Woche 1: CSV‑Daten + Exploration  
- [ ] Woche 2: API‑Daten + Modellierung  
- [ ] Woche 3: Dashboard + Storytelling

---

## 📌 Projektübersicht
Dieses Projekt untersucht Musiknutzungstrends anhand von Spotify‑Daten.  
Dazu werden **Charts‑CSVs**, **Spotify Web API‑Metadaten**, **Feature Engineering**, **Forecast‑Modelle** und ein **Plotly‑Dashboard** kombiniert.  
Ziel ist ein vollständiges **End‑to‑End Data‑Science‑Portfolio‑Projekt**, das Daten, KI und Storytelling verbindet.

---

## 🚀 Features
- Analyse von Spotify‑Charts (CSV‑Daten)
- Abruf von Metadaten über die Spotify Web API (Genres, Popularität, Follower)
- Feature Engineering (Genre Popularity Index, Artist Growth Rate, Seasonality Score)
- Zeitreihen‑Forecasts (ARIMA, Prophet, LSTM)
- Klassifikation von „Rising Artists“
- Interaktives Dashboard (Plotly Dash)
- Automatisch generierte Trendberichte (LLM‑Integration)
- Vollständig reproduzierbar via Docker

---

## 📁 Projektstruktur
```
musiktrends-spotify/
│
├── data/          # Rohdaten, CSVs, API-Downloads (aktuell nicht verfügbar)
├── notebooks/     # Jupyter Notebooks für Exploration & Modellierung
├── src/           # Python-Module (Pipelines, Modelle, Utils)
├── docs/          # Dokumentation, Diagramme, Berichte
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🗂️ Datenquellen
### **Spotify Charts (CSV)**
- Daily & Weekly Top 200  
- Direkt importierbar in Pandas

### **Spotify Web API**
- Künstler‑Metadaten  
- Audio‑Features  
- Popularität & Follower  
- Genre‑Informationen  

---

## 🧠 Modellierung
### **Zeitreihen‑Forecasts**
- ARIMA  
- Prophet  
- LSTM  

### **Klassifikation**
- Random Forest  
- Logistic Regression  
- Gradient Boosting  

---

## 📊 Dashboard
Das interaktive Dashboard zeigt:
- Genre‑Heatmaps  
- Forecast‑Kurven  
- KPIs für „Rising Artists“  
- Automatisch generierte Trendberichte  

---

## 🐳 Docker Setup
### Build
```
docker build -t spotify-trends .
```

### Run (Jupyter Notebook)
```
docker run -p 8888:8888 spotify-trends
```

---

## 🛠 Installation (lokal)
```
pip install -r requirements.txt
```

---

## 📄 Lizenz
MIT License 

---

## 🤝 Mitwirken
Pull Requests und Issues sind willkommen.

