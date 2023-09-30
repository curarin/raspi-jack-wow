# E-Paper-Performance-Dashboard für World of Warcraft

## Beschreibung

Hierbei handelt es sich um ein Raspberry Pi Projekt. Aggregiert WoW-Performance-Daten über APIs (Raider.io, Warcraftlogs.com) und visualisiert sie auf einem E-Paper-Display. Software läuft auf einem Raspberry Pi Zero W. Für die Programmierung wurde Python verwendet. 

## Resultat

## Funktionsweise Hardware

## Funktionsweise Software
Die Software besteht aus drei Python-Scripts. Daten werden temporär in einer lokalen SQLite3 Datenbank auf einer SD-Karte gespeichert.

### Verwendete Python Scripts

#### georg_wow_etl.py
Holt durch die User:innen hinterlegte Charakter-/ und Server-Informationen aus der Datenbank, übergibt sie an die jeweiligen Schnittstellen und generiert tagesaktuelle Daten.

Daten werden aus zwei verschiedenen Quellen mittels API geholt:
- Warcraftlogs.com
- Raider.io

Folgende generische Daten werden dabei von **Warcraftlogs.com** für jeden hinterlegten Charakter geholt:
- Performance Percentile Average pro Charakter für das aktuelle Raid-Tier
- Performance Percentile Median pro Charakter für das aktuelle Raid-Tier

Folgende Encounter-spezifische Daten werden von **Warcraftlogs.com** für jeden hinterlegten Charakter geholt:
- Name per Encounter
- Gesamt-Kill-Count per Encounter
- Performance Maximum Percentile per Encounter
- World Rank per Encounter (Allstars-Ranking)
- Region Rank per Encounter (Allstars-Ranking)
- Realm Rank per Encounter (Allstars-Ranking)

Das Skript wird mittels Cronjob 1x täglich ausgeführt:
- 0 4 * * * /usr/bin/python3 /home/paulherzog/python/georg_wow_etl.py

 ### SQLite3 DB Struktur
