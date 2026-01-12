# Analyse-Bericht: Zeitreihen-Analyse & Modell-Validierung (Woche 2)

## 1. Auswertung der Prophet-Komponenten

Die Zerlegung der Zeitreihe in ihre Einzelteile liefert tiefe Einblicke in die Mechanik des Streaming-Marktes:

* **Trend (Langfristige Richtung):** Die Analyse zeigt einen starken Anstieg bis Mitte 2024, gefolgt von einem leichten Abfall und einer Stabilisierung ab 2025. Dies repräsentiert das "Grundrauschen" des Marktes nach einem massiven Wachstumsschub.
* **Holidays (Schock-Events):** Steile Ausschläge von über 30 % markieren den Effekt von "Feiertagen" wie Taylor Swift Releases oder Weihnachten. Das Modell ordnet diesen spezifischen Tagen massive Stream-Zunahmen im Vergleich zum Normaltrend zu.
* **Yearly (Saisonalität):** Ein Wellenmuster verdeutlicht das kollektive Hörerverhalten: Ein hohes Niveau zu Jahresbeginn (Nachwirkungen von Weihnachten und Silvester), ein Tief im Sommer und ein steiler Anstieg im Dezember.
* **Extra Regressors (Genre Popularity Index):** Eine zackige Linie im Bereich von 0 % bis 20 % zeigt den Einfluss der Genre-Beliebtheit auf das Gesamtvolumen. Ein Abfall Ende 2025 deutet auf einen sinkenden Einfluss der Genres in diesem Zeitraum hin.
* **Gesamt-Forecast:** Das Modell kombiniert historische Daten (schwarze Punkte) mit der Schätzung (blaue Linie). Es erklärt extreme Spitzen präzise durch die Holiday-Komponente und liefert eine valide Prognose für die kommenden Wochen.

## 2. Interpretation der Modellparameter

Durch das Hyperparameter-Tuning wurden die optimalen Einstellungen für die Volatilität des Musikmarktes gefunden:

* **`changepoint_prior_scale = 0.5` (Sehr flexibler Trend):** Erlaubt dem Modell, schnell auf häufige Trendwechsel zu reagieren. Dies ist essenziell für den Musikmarkt, da Superstar-Releases und Viral-Hits den Trend oft abrupt sprengen.
* **`holidays_prior_scale = 10.0` (Starke Holiday-Effekte):** Gibt Events massives Gewicht und verhindert, dass extreme Peaks den langfristigen Trend verzerren. Ohne diese Gewichtung würde der Forecast an Genauigkeit verlieren.
* **`seasonality_mode = 'multiplicative'`:** Die richtige Wahl für Streaming, da der Markt prozentual wächst und Saisonalität (z. B. Sommerloch oder Q4-Push) verstärkend wirkt.

## 3. Performance-Metriken

Die statistische Validierung bestätigt die hohe Güte des Modells:

| Metrik | Wert | Interpretation |
| --- | --- | --- |
| **MAPE** | **0.06** | Ein Fehler von nur 6 % liegt im "Goldstandard-Bereich" für reales Markt-Forecasting. |
| **RMSE** | **188.175.034** | Bei einem Wochenvolumen von ca. 3–4 Mrd. Streams entspricht dieser absolute Fehler etwa 5 %. |

## Fazit & Ausblick

Das entwickelte Modell sagt globale Streaming-Trends mit einer **Genauigkeit von 94 %** vorher. Es erkennt, dass der Markt zwar stabil ist, aber massiv durch Events und Genre-Dynamiken gesteuert wird.