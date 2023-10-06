# E-Paper-Performance-Dashboard für World of Warcraft

## Beschreibung

Hierbei handelt es sich um ein Raspberry Pi Projekt. Aggregiert WoW-Performance-Daten über APIs (Raider.io, Warcraftlogs.com) und visualisiert sie auf einem E-Paper-Display. Software läuft auf einem Raspberry Pi Zero W. Für die Programmierung wurde Python verwendet. 

## Resultat

## Funktionsweise Hardware

## Funktionsweise Software
Die Software besteht aus drei Python-Scripts. Daten werden temporär in einer lokalen SQLite3 Datenbank auf einer SD-Karte gespeichert.

### Verwendete Python Scripts
Es werden in Summe drei Skripte verwendet:
- **georg_wow_etl.py** für den gesamten ETL-Prozess (Daten extrahieren, transformieren und laden)
- **wow_plotting.py** für das Erstellen tagesaktueller Grafiken / Plots
- **wow_epaper.py** für das Visualisieren aller Informationen auf dem E-Paper-Display sowie das Ansteuern über Buttons.

#### georg_wow_etl.py
Holt manuell hinterlegte Charakter-/ und Server-Informationen aus der Datenbank, übergibt sie an die jeweiligen Schnittstellen und generiert tagesaktuelle Daten.

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
 Die SQLite3-Datenbank besteht aus zwei Tables.

 - Character Names
 - API Data

 #### Character Names
 | ID  | NAME  | REALM  |
| ------------- |:-------------:| -----:|
| 1 | jackbrew | silvermoon |
| 2 | jackbear | silvermoon |
| 3 | jackazzem | silvermoon |
| 4 | jackpaladin | silvermoon |
| 5 | jackblud | silvermoon |
| 6 | jackdark | silvermoon |


 #### Table 2
 API Data besteht aus mehreren hundert Kolumnen. Hier werden die Daten aus der API gespeichert, um sie dann im nächsten Schritt verarbeiten zu können.

 Tabelle sieht circa wie folgt aus:
 | wcl_performance_average  | wcl_performance_median  | encounter_1_name  | encounter_1_rank_percent | encounter_1_median_percent | ... |
| ------------- |-------------| |-------------| |-------------||-------------|-----|
| 1 | 91.15 | 82.56 | Kazzara, the Hellforged | 98.73 | 88.51 | ... |
| 2 | 89.80 | 83.91 | Kazzara, the Hellforged | 94.70 | 92.22 | ... |


 ### Hinweise für die Nutzung

 #### Internet / Konnektivität
 Die "Hall of Fame"-Konstruktion benötigt für das Ausführen der **georg_wow_etl.py**-Datei Internet-Zugang. Diese wird jeden Tag um 04:00 uhr Früh gestartet und lädt aktuelle Daten aus den Warcraftlogs- und Raider.IO-Datenbanken.

 Da diese Daten dann anschließend in der internen SQLite3-Datenbank zwischengespeichert werden, wird für das bloße Bedienen sowie Daten-Anzeigen zwischen den Charakteren keine Internet-Verbindung benötigt.


 #### Stromversorgung
 E-Paper-Displays benötigen Strom ausschließlich für das Wechseln von Informationen - nicht für die reine Anzeige. Dadurch bleiben Informationen auf dem Display ersichtlich, selbst wenn die "Hall of Fame"-Konstruktion aktuell nicht mit Strom versorgt ist.

 Durch die Neuversorgnung mit Strom (beispielsweise nach einem Transport) wird der im Technik-Raum befindliche Raspberry Pi neugestartet. Bei Neustart wird automatisiert das Script **wow_epaper.py** gestartet, welches für die Anzeige aller Informationen auf dem E-Paper-Display sowie das Steuern über Buttons verantwortlich ist.

 Dieser Vorgang (Hochfahren + Script starten) dauert rund 2 Minuten.


 #### Charakter Transfer
 Wenn Charakter transferiert werden muss zwingend die Datenbank mit den Charakter-Namen angepasst werden. Aus dieser Tabelle erhält das ETL-Script die notwendigen Charakter-spezifischen Informationen, um anschließend auf Warcraftlogs sowie Raider.io die richtigen Daten zu finden.

 So passt du deine Charakter-Daten an:

 - Schritt 1: Öffne das Terminal auf deinem Mac (Mac-Suche "Terminal")
 - Schritt 2: Stelle eine Verbindung mit dem Raspberry Pi her, indem du folgenden Command eingibst:
 
```
ssh paulherzog@raspberrypi.local
```

- Schritt 3: Gib das von mir kommunizierte Passwort ein. Du siehst beim Eingeben keine Zeichen - keine Sorge, das passt schon so.
- Schritt 4: Nach dem erfolgreichen Connecten wechselst du in das Verzeichnis der SQL-Datenbank. Dafür gibst du folgenden Befehl ein:

```
cd sql_databases
```
- Schritt 5: Öffne die Datenbank, in denen deine Daten gespeichert sind. Dazu gibst du nun folgenden Begriff ein:
```
sqlite3 jack_wow.db
```
- Schritt 6: Nun gibst du folgende SQL-Query ein und passt dabei die ID auf die [Tabelle mit den Charakter-Daten](https://github.com/curarin/raspi-jack-wow#character-names) an.

**Ein paar Beispiele:**
- Dein Monk ist in der Tabelle in Zeile 1 gespeichert. Er trägt also die ID "1". Nun wechselst du den Server, der Name bleibt jedoch ident. Daher gibst du nun folgendes ein:
```
UPDATE char_names SET REALM = "name-des-neuen-servers" WHERE ID = 1;
```
- Wenn sich nun der Name des Monks ebenfalls ändern sollte, führst du die selbe SQL-Query nochmals aus - jedoch mit angepassten Daten. Dieses Mal änderst du den Namen des Monks:
```
UPDATE char_names SET NAME = "neuer-name-des-monks" WHERE ID = 1;
```
- Dies wird nun für [alle Charaktere](https://github.com/curarin/raspi-jack-wow#character-names) durchgeführt.
- Anschließend kannst du mit nachfolgender SQL-Query überprüfen, ob die Daten nun korrekt angepasst wurden.
```
SELECT * FROM char_names;
```

**Wichtiger Hinweis:** Aktualisiere ASAP deine Profile auf Warcraftlogs.com sowie Raider.IO, damit die Daten am nächsten Tag erfolgreich geholt werden können.