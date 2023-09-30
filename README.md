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

##### Warcraftlogs Daten
**Generische Daten:**
- Performance Percentile Average pro Charakter für das aktuelle Raid-Tier
- Performance Percentile Median pro Charakter für das aktuelle Raid-Tier

**Encounter-spezifische Daten:**
- Name per Encounter
- Gesamt-Kill-Count per Encounter
- Performance Maximum Percentile per Encounter
- World Rank per Encounter (Allstars-Ranking)
- Region Rank per Encounter (Allstars-Ranking)
- Realm Rank per Encounter (Allstars-Ranking)
- Fastest Kill Time per Encounter

##### Raider.io Daten
**Generische Daten:**
- Name
- Klasse
- Guilde
- Realm
- Fraktion
- ItemLevel
- RaiderIO-Punkte (RIO)
- M+ Rankings Gesamt (World, Region, Realm)
- Raid Progress Summary (z.B. 9/9 M)
- Dungeon-Performance-Daten: Höchstes Mythic-Plus-Level, Datum des höchsten Abschlusses, Clear Time, Upgrade-Level (z.B. +1, +2 oder +3) sowie URL zum besten Run

##### Automatisierung
Das Skript wird mittels Cronjob täglich um 04:00 Uhr (A.M.) ausgeführt:
- 0 4 * * * /usr/bin/python3 /home/paulherzog/python/georg_wow_etl.py

 ### SQLite3 DB Struktur


 ### Hinweise für die Nutzung

 #### Internet / Konnektivität

 #### Stromversorgung

 #### Charakter Transfer
 Wenn Charakter transferiert werden muss zwingend die Datenbank mit den Charakter-Namen angepasst werden. Aus dieser Tabelle erhält das ETL-Script die notwendigen Charakter-spezifischen Informationen, um anschließend auf Warcraftlogs sowie Raider.io die richtigen Daten zu finden.

 