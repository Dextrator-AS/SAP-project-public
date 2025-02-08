import pandas as pd

# Datei-Pfade
file_paths = ["oura-activity.json", "oura-readiness.json", "oura-sleep.json"]

# Daten laden und verarbeiten
dataframes = []
for file_path in file_paths:
    try:
        df = pd.read_json(file_path)
        if 'daily_activity' in df.columns:
            # Entpacke Aktivitätsdaten
            df = pd.json_normalize(df['daily_activity'])
            print(f"JSON file '{file_path}' processed as 'daily_activity'")
        elif 'daily_readiness' in df.columns:
            # Entpacke Readiness-Daten
            df = pd.json_normalize(df['daily_readiness'])
            print(f"JSON file '{file_path}' processed as 'daily_readiness'")
        elif 'daily_sleep' in df.columns:
            # Entpacke Schlafdaten
            df = pd.json_normalize(df['daily_sleep'])
            print(f"JSON file '{file_path}' processed as 'daily_sleep'")
        else:
            print(f"JSON file '{file_path}' does not have the expected keys.")
            continue
        dataframes.append(df)
    except ValueError as e:
        print(f"Error loading JSON file '{file_path}': {e}")

# Überprüfen, ob Daten erfolgreich geladen wurden
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    print("All files successfully combined.")
    print("Spalten in combined_df:", combined_df.columns)
else:
    raise ValueError("No data loaded from the files.")

# Sicherstellen, dass die Spalte 'day' vorhanden ist
if 'day' in combined_df.columns:
    combined_df['timestamp'] = pd.to_datetime(combined_df['day'])
else:
    raise KeyError("Die Spalte 'day' wurde nicht gefunden. Überprüfe die JSON-Daten.")

# Aktivitätsdaten vorbereiten
if 'active_calories' in combined_df.columns:
    activities = combined_df[['day', 'active_calories', 'average_met_minutes', 'low_activity_time', 'medium_activity_time', 'high_activity_time']].copy()
    activities['date'] = pd.to_datetime(activities['day']).dt.date
    daily_activities = activities.groupby('date').agg({
        'active_calories': 'sum',
        'average_met_minutes': 'mean',
        'low_activity_time': 'sum',
        'medium_activity_time': 'sum',
        'high_activity_time': 'sum'
    }).reset_index()
else:
    daily_activities = None

# Readiness-Daten vorbereiten
if 'score' in combined_df.columns:
    readiness = combined_df[['day', 'score']].copy()
    readiness['date'] = pd.to_datetime(readiness['day']).dt.date
else:
    readiness = None

# Schlafdaten vorbereiten
if 'contributors.deep_sleep' in combined_df.columns:
    sleep = combined_df[['day', 'contributors.deep_sleep', 'contributors.rem_sleep', 'contributors.total_sleep']].copy()
    sleep.rename(columns={
        'contributors.deep_sleep': 'deep_sleep',
        'contributors.rem_sleep': 'rem_sleep',
        'contributors.total_sleep': 'total_sleep'
    }, inplace=True)
    sleep['date'] = pd.to_datetime(sleep['day']).dt.date
else:
    sleep = None

# Prüfen, ob alle notwendigen Daten geladen wurden
if readiness is None or sleep is None or daily_activities is None:
    print("\nNicht genügend Daten für die Analyse. Debugging-Daten:")
    print(f"Readiness DataFrame: {readiness.shape if readiness is not None else 'No data'}")
    print(f"Sleep DataFrame: {sleep.shape if sleep is not None else 'No data'}")
    print(f"Activities DataFrame: {daily_activities.shape if daily_activities is not None else 'No data'}")
else:
    # Daten zusammenführen
    merged_df = readiness.merge(sleep, on='date', suffixes=('_readiness', '_sleep'))
    merged_df = merged_df.merge(daily_activities, on='date', how='left')

    # Einfluss analysieren
correlation_calories_readiness = merged_df['active_calories'].corr(merged_df['score']) if 'active_calories' in merged_df.columns else None
correlation_deep_sleep_readiness = merged_df['deep_sleep'].corr(merged_df['score']) if 'deep_sleep' in merged_df.columns else None
correlation_rem_sleep_readiness = merged_df['rem_sleep'].corr(merged_df['score']) if 'rem_sleep' in merged_df.columns else None
correlation_calories_sleep = merged_df['active_calories'].corr(merged_df['total_sleep']) if 'total_sleep' in merged_df.columns else None

# Ergebnisse ausgeben
print("\nKorrelationen:")
if correlation_calories_readiness is not None:
    print(f"Active Calories vs. Readiness Score: {correlation_calories_readiness:.2f}")
if correlation_deep_sleep_readiness is not None:
    print(f"Deep Sleep vs. Readiness Score: {correlation_deep_sleep_readiness:.2f}")
if correlation_rem_sleep_readiness is not None:
    print(f"REM Sleep vs. Readiness Score: {correlation_rem_sleep_readiness:.2f}")
if correlation_calories_sleep is not None:
    print(f"Active Calories vs. Total Sleep: {correlation_calories_sleep:.2f}")

# Zusammenfassung der Ergebnisse
print("\nAntwort auf die Frage:")
if correlation_calories_readiness is not None:
    if correlation_calories_readiness > 0.5:
        print("Ihre täglichen Aktivitäten (Active Calories) haben einen starken positiven Einfluss auf Ihren Readiness Score.")
    elif correlation_calories_readiness > 0:
        print("Ihre täglichen Aktivitäten (Active Calories) haben einen leichten positiven Einfluss auf Ihren Readiness Score.")
    else:
        print("Ihre täglichen Aktivitäten (Active Calories) haben keinen klaren oder einen negativen Einfluss auf Ihren Readiness Score.")

if correlation_calories_sleep is not None:
    if correlation_calories_sleep > 0.5:
        print("Ihre täglichen Aktivitäten (Active Calories) haben einen starken positiven Einfluss auf Ihre Schlafqualität (Total Sleep).")
    elif correlation_calories_sleep > 0:
        print("Ihre täglichen Aktivitäten (Active Calories) haben einen leichten positiven Einfluss auf Ihre Schlafqualität (Total Sleep).")
    else:
        print("Ihre täglichen Aktivitäten (Active Calories) haben keinen klaren oder einen negativen Einfluss auf Ihre Schlafqualität (Total Sleep).")

if correlation_deep_sleep_readiness is not None:
    if correlation_deep_sleep_readiness > 0.5:
        print("Ihre Tiefschlafphasen haben einen starken positiven Einfluss auf Ihren Readiness Score.")
    elif correlation_deep_sleep_readiness > 0:
        print("Ihre Tiefschlafphasen haben einen leichten positiven Einfluss auf Ihren Readiness Score.")
    else:
        print("Ihre Tiefschlafphasen haben keinen klaren oder einen negativen Einfluss auf Ihren Readiness Score.")

if correlation_rem_sleep_readiness is not None:
    if correlation_rem_sleep_readiness > 0.5:
        print("Ihre REM-Schlafphasen haben einen starken positiven Einfluss auf Ihren Readiness Score.")
    elif correlation_rem_sleep_readiness > 0:
        print("Ihre REM-Schlafphasen haben einen leichten positiven Einfluss auf Ihren Readiness Score.")
    else:
        print("Ihre REM-Schlafphasen haben keinen klaren oder einen negativen Einfluss auf Ihren Readiness Score.")

# Optionale Ausgabe der kombinierten Tabelle
print("\nZusammengeführte Daten:")
print(merged_df.head())

# Berechnung der Korrelationen
correlations = {
    "Metric 1": [],
    "Metric 2": [],
    "Correlation": []
}

# Hinzufügen von Korrelationen zu den Ergebnissen
if 'active_calories' in merged_df.columns and 'score' in merged_df.columns:
    correlations["Metric 1"].append("Active Calories")
    correlations["Metric 2"].append("Readiness Score")
    correlations["Correlation"].append(merged_df['active_calories'].corr(merged_df['score']))

if 'deep_sleep' in merged_df.columns and 'score' in merged_df.columns:
    correlations["Metric 1"].append("Deep Sleep")
    correlations["Metric 2"].append("Readiness Score")
    correlations["Correlation"].append(merged_df['deep_sleep'].corr(merged_df['score']))

if 'rem_sleep' in merged_df.columns and 'score' in merged_df.columns:
    correlations["Metric 1"].append("REM Sleep")
    correlations["Metric 2"].append("Readiness Score")
    correlations["Correlation"].append(merged_df['rem_sleep'].corr(merged_df['score']))

if 'active_calories' in merged_df.columns and 'total_sleep' in merged_df.columns:
    correlations["Metric 1"].append("Active Calories")
    correlations["Metric 2"].append("Total Sleep")
    correlations["Correlation"].append(merged_df['active_calories'].corr(merged_df['total_sleep']))

# Tabelle der Korrelationen erstellen
correlation_df = pd.DataFrame(correlations)

# Ausgabe der Tabelle
print("\nTabelle der Korrelationen:")
print(correlation_df)

# Erklärung der Korrelation
print("\nWas bedeuten diese Korrelationen?")
print(
    """
Eine Korrelation misst, wie stark zwei Variablen miteinander zusammenhängen:
- Werte reichen von -1 bis 1.
  - 1: Perfekte positive Korrelation – wenn eine Variable steigt, steigt die andere.
  - -1: Perfekte negative Korrelation – wenn eine Variable steigt, sinkt die andere.
  - 0: Keine Korrelation – die Variablen hängen nicht zusammen.
- Typische Interpretation:
  - 0.7 bis 1.0 oder -0.7 bis -1.0: Starke Korrelation.
  - 0.4 bis 0.7 oder -0.4 bis -0.7: Mittlere Korrelation.
  - 0.1 bis 0.4 oder -0.1 bis -0.4: Schwache Korrelation.
  - 0: Kein Zusammenhang.
"""
)

# Optional: Tabelle in eine Datei speichern
correlation_df.to_csv("correlation_results.csv", index=False)
print("\nDie Tabelle der Korrelationen wurde als 'correlation_results.csv' gespeichert.")


