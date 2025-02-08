import pandas as pd
import json
from datetime import datetime

# Lade die JSON-Dateien
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Lade die Standortquadrate aus einer TXT-Datei
def load_location_zones(file_path):
    zones = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        current_zone = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if any(c.isalpha() for c in line):
                current_zone = line
                zones[current_zone] = []
            else:
                lat, lon = map(float, line.split(", "))
                zones[current_zone].append((lat, lon))
    return zones

# Standortdaten, Schlafdaten und Standortzonen laden
location_data = load_json("oura-location.json")
sleep_data = load_json("oura-sleep.json")
location_zones = load_location_zones("locations.txt")

# In DataFrames umwandeln
location_df = pd.DataFrame(location_data["smoothed_location"])
sleep_df = pd.DataFrame(sleep_data["daily_sleep"])

# Konvertiere Timestamp-Strings zu datetime-Objekten
location_df["timestamp"] = pd.to_datetime(location_df["timestamp"], utc=True)
sleep_df["day"] = pd.to_datetime(sleep_df["day"])

# Filtere Standortdaten auf Abendzeiten (z.B. nach 18:00 Uhr)
location_df["hour"] = location_df["timestamp"].dt.hour
night_locations = location_df[location_df["hour"] >= 18]

# Finde den letzten Standort für jeden Tag
last_locations = night_locations.sort_values("timestamp").groupby(location_df["timestamp"].dt.date).last().reset_index(drop=True)
last_locations["day"] = pd.to_datetime(last_locations["timestamp"].dt.date)

# Schlafdaten mit Standorten mergen
merged_df = pd.merge(last_locations, sleep_df, on="day", how="inner")

# Gruppiere nach Standortquadraten
def assign_location(lat, lon, zones):
    for zone, coords in zones.items():
        if any(abs(lat - c[0]) < 0.0005 and abs(lon - c[1]) < 0.0005 for c in coords):
            return zone
    return "ZuHause Sankt Leon"

merged_df["Location"] = merged_df.apply(lambda row: assign_location(row["latitude"], row["longitude"], location_zones), axis=1)

# Berechne durchschnittlichen Schlafscore pro Standort
sleep_by_location = merged_df.groupby("Location")["score"].mean().reset_index()
sleep_by_location.columns = ["Location", "Average Sleep Score"]

# Besten Schlafort bestimmen
best_location = sleep_by_location.loc[sleep_by_location["Average Sleep Score"].idxmax()]

# Ergebnisse ausgeben
print("Durchschnittlicher Schlafscore pro Standort:")
print(sleep_by_location)
print("\nBester Standort für Schlaf:")
print(best_location)
