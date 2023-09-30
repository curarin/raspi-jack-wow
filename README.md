# E-Paper-Performance-Dashboard für World of Warcraft

## Beschreibung

Hierbei handelt es sich um ein Raspberry Pi Projekt für Georg. Aggregiert WoW-Performance-Daten über APIs (Raider.io, Warcraftlogs.com) und visualisiert sie auf einem E-Paper-Display. Software läuft auf einem Raspberry Pi Zero W. Für die Programmierung wurde Python verwendet. 

## Resultat

## Funktionsweise Hardware

## Funktionsweise Software
Die Software besteht aus drei Python-Scripts. Daten werden temporär in einer lokalen SQLite3 Datenbank auf einer SD-Karte gespeichert.

### Verwendete Python Scripts

#### georg_wow_etl.py
Holt durch die User:innen hinterlegte Charakter-/ und Server-Informationen aus der Datenbank, übergibt sie an die jeweiligen Schnittstellen und generiert tagesaktuelle Daten.

Das Skript wird mittels Cronjob 1x täglich ausgeführt:
- 0 4 * * * /usr/bin/python3 /home/paulherzog/python/georg_wow_etl.py

 ### SQLite3 DB Struktur
