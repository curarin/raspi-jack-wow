import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime
import epaper


##### DRIVERS AND INITIALIZING DISPLAY########
#epd = epaper.epaper("epd7in5_V2").EPD() # get the display
#epd.init()           # initialize the display
#print("Resetting display...")    # prints to console, not the display, for debugging
#epd.reset()      # clear the display
######## CONNECT TO DB
### READ CHAR NAMES FROM table "char_names" in db "jack_wow"
# Read data from the database
connection_obj = sqlite3.connect("/home/paulherzog/sql_databases/jack_wow.db")
cursor_obj = connection_obj.cursor()
print("Connected to jack_wow.db.")
statement = """SELECT * FROM char_names"""
cursor_obj.execute(statement)
print("Fetching character name data from table...")
output = cursor_obj.fetchall()
df_char_names = pd.DataFrame(columns=["ID", "CharName", "Realm"])
for row in output:
    df_char_names = df_char_names.append({"ID": row[0], "CharName": row[1], "Realm": row[2]}, ignore_index=True)
print("...successfully retrieved character name data.")
#now check what the current raid is from sqlite3 table
raid_release_dates_statement = """SELECT name, first_seen FROM raid_names; """
cursor_obj.execute(raid_release_dates_statement)
raid_release_dates_db_data = cursor_obj.fetchall()
raid_release_dates_df = pd.DataFrame(columns=["name", "first_seen"])
for row in raid_release_dates_db_data:
    raid_release_dates_df = raid_release_dates_df.append({"name":row  [0], "first_seen": row[1]}, ignore_index=True)
raid_release_dates_df["first_seen"] = pd.to_datetime(raid_release_dates_df["first_seen"], format="%d-%m-%Y")
list_with_db_raid_names = list(raid_release_dates_df["name"]) #die liste wird spaeter gebraucht um zu checken ob was neues dazugekommen ist
print("Successfully fetched Raid Names & Release Dates from DB")
connection_obj.close()
print("Connection to jack_wow.db closed.")

# Warcraftlogs Credentials & AUTH via POST
client_id_warcraftlogs = "9a265d81-2881-4d13-876d-556ead93a858"
client_secret_warcraftlogs = "JX2pF4kThvnBaDN20W9ZufpoaRVmFWmUkLG61vjF"
token_url_warcraftlogs = "https://www.warcraftlogs.com/oauth/token"
data_warcraftlogs = {
	"grant_type": "client_credentials"
}
auth_warcraftlogs = (client_id_warcraftlogs, client_secret_warcraftlogs)
response_warcraftlogs = requests.post(token_url_warcraftlogs, data=data_warcraftlogs, auth=auth_warcraftlogs)

####
# build a list
character_data_list = []

# Loop through APIs to get data for each character
for char in df_char_names.itertuples(index=False):
        region = "eu"
        char_name = char.CharName
        realm = char.Realm

        # API URLs
        api_url_raider_io = f"https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={char_name}&fields=gear%2Cguild%2Craid_progression%2Cmythic_plus_ranks%2Cmythic_plus_best_runs%2Cmythic_plus_scores_by_season:current"
        api_url_warcraftlogs = "https://www.warcraftlogs.com/api/v2/client"

        # Warcraftlogs API Request
        if response_warcraftlogs.status_code == 200:
                access_token_warcraftlogs = response_warcraftlogs.json().get("access_token")
                headers_warcraftlogs = {
                        "Authorization": f"Bearer {access_token_warcraftlogs}",
                        "Content-Type": "application/json" 
                }
                graphql_query_warcraftlogs = graphql_query_warcraftlogs = '{ characterData { character' + f'(name: "{char_name}", serverSlug: "{realm}", serverRegion: "{region}"' + '){ id canonicalID zoneRankings } } }'

                query_data_warcraftlogs = {
                        "query": graphql_query_warcraftlogs
                }
                api_response_warcraftlogs = requests.get(api_url_warcraftlogs, headers=headers_warcraftlogs, json=query_data_warcraftlogs)

                # Process the API response as needed
                if api_response_warcraftlogs.status_code == 200:
                        api_data_warcraftlogs = api_response_warcraftlogs.json()
                        print(f"Warcraftlogs data successfully fetched for {char_name}.")
                # Process the data here
                else:
                        print("API request failed with status code:", api_response_warcraftlogs.status_code)
        else:
                print("Token request failed with status code:", api_response_warcraftlogs.status_code)

        
        # Encounter Data from Warcraftlogs
        wclogs_zonerankings_bestavg = api_data_warcraftlogs["data"]["characterData"]["character"]["zoneRankings"]["bestPerformanceAverage"]
        if wclogs_zonerankings_bestavg is not None:
            wclogs_zonerankings_bestavg = f"{wclogs_zonerankings_bestavg:.2f}"
        wclogs_zonerankings_medianavg = api_data_warcraftlogs["data"]["characterData"]["character"]["zoneRankings"]["medianPerformanceAverage"]
        if wclogs_zonerankings_medianavg is not None:
            wclogs_zonerankings_medianavg = f"{wclogs_zonerankings_medianavg:.2f}"
        encounters_warcraftlogs = api_data_warcraftlogs["data"]["characterData"]["character"]["zoneRankings"]["rankings"]

        ### looping through encounter data

        ### build the caracter data
        character_data = {
            "wcl_performance_average": wclogs_zonerankings_bestavg,
            "wcl_performance_median": wclogs_zonerankings_medianavg            
        }
        

        for i, encounter_data in enumerate(encounters_warcraftlogs, start=1):
            if encounter_data is None or not isinstance(encounter_data, dict):
                # Handle the case where encounter_data is not a dictionary or is None
                continue

            encounter_name = encounter_data.get('encounter', {}).get('name', 'N/A')
            character_data[f'encounter_{i}_name'] = encounter_name

            encounter_medianPercent = encounter_data.get("medianPercent", 'N/A')
            if encounter_medianPercent is not None:
                try:
                    encounter_medianPercent = f"{encounter_medianPercent:.2f}"
                except (ValueError, TypeError):
                    encounter_medianPercent = "N/A"
            character_data[f'encounter_{i}_median_percent'] = encounter_medianPercent

            encounter_totalkills = encounter_data.get("totalKills", 'N/A')
            character_data[f'encounter_{i}_totalkills'] = encounter_totalkills


            allStars_data = encounter_data.get("allStars")
            if allStars_data is not None and isinstance(allStars_data, dict):
                encounter_worldrank = allStars_data.get("rank", 'N/A')
                character_data[f'encounter_{i}_worldrank'] = encounter_worldrank


                encounter_regionrank = allStars_data.get("regionRank", 'N/A')
                character_data[f'encounter_{i}_regionrank'] = encounter_regionrank


                encounter_serverrank = allStars_data.get("serverRank", 'N/A')
                character_data[f'encounter_{i}_serverrank'] = encounter_serverrank


                encounter_rankpercent = allStars_data.get("rankPercent", 'N/A')
                if encounter_rankpercent is not None:
                    try:
                        encounter_rankpercent = f"{encounter_rankpercent:.2f}"
                    except (ValueError, TypeError):
                        encounter_rankpercent = "N/A"
                character_data[f'encounter_{i}_rankpercent'] = encounter_rankpercent

            else:
                # Handle the case where allStars_data is not a dictionary or is None
                encounter_worldrank = 0.0
                character_data[f'encounter_{i}_worldrank'] = encounter_worldrank
                encounter_regionrank = 0.0
                character_data[f'encounter_{i}_regionrank'] = encounter_regionrank
                encounter_serverrank = 0.0
                character_data[f'encounter_{i}_serverrank'] = encounter_serverrank
                encounter_rankpercent = 0.0
                character_data[f'encounter_{i}_rankpercent'] = encounter_rankpercent

            encounter_fastestkill = encounter_data.get("fastestKill", 'N/A')            
            if encounter_fastestkill:
                try:
                    minutes, seconds = divmod(encounter_fastestkill // 1000, 60)
                    encounter_fastestkill = f"{minutes:02}:{seconds:02}"
                except (ValueError, TypeError):
                    encounter_fastestkill = "N/A"
            character_data[f'encounter_{i}_fastestkilltime'] = encounter_fastestkill
            #print(f"{encounter_name} Performance: {encounter_rankpercent}. Total Kills: {encounter_totalkills} | World Rank: {encounter_worldrank} | Region Rank: {encounter_regionrank} | Server Rank: {encounter_serverrank} | Fastest Kill: {encounter_fastestkill}")

# Make the API request for raider.io
        response_raider_io = requests.get(api_url_raider_io)

        if response_raider_io.status_code == 200:
                character_data_raider_io = response_raider_io.json()
                print(f"Raider.io data successfully fetched for {char_name}.")
                #print(json.dumps(character_data_raider_io, indent=4)))
        else:
                print(f"Failed to fetch character data. Status code: {response_raider_io.status_code}")
                
        #RAIDER . IO DATA EXTRACTION
        character_data["charname"] = character_data_raider_io["name"]
        character_data["charclass"] = character_data_raider_io["class"]
        character_data["charthumbnail"] = character_data_raider_io["thumbnail_url"]
        character_data["charguild"] = character_data_raider_io["guild"]["name"]
        character_data["charrealm"] = character_data_raider_io["guild"]["realm"]
        char_faction = character_data_raider_io["faction"]
        if char_faction == "alliance":
            char_faction = "Alliance"
        else:
            char_faction = "Horde"
        character_data["charfaction"] = char_faction
        character_data["charilevel"] = character_data_raider_io["gear"]["item_level_equipped"]
        character_data["charachievementpoints"] = character_data_raider_io["achievement_points"]
        character_data["mplus_rio"] = character_data_raider_io["mythic_plus_scores_by_season"][0]["scores"]["all"]
        character_data["mplus_rankings_world"] = character_data_raider_io["mythic_plus_ranks"]["overall"]["world"]
        character_data["mplus_rankings_region"] = character_data_raider_io["mythic_plus_ranks"]["overall"]["region"]
        character_data["mplus_rankings_realm"] = character_data_raider_io["mythic_plus_ranks"]["overall"]["realm"]
        character_data["mplus_rankings_class_world"] = character_data_raider_io["mythic_plus_ranks"]["class"]["world"]
        character_data["mplus_rankings_class_region"] = character_data_raider_io["mythic_plus_ranks"]["class"]["region"]
        character_data["mplus_rankings_class_realm"] = character_data_raider_io["mythic_plus_ranks"]["class"]["realm"]
        #m_plus_dungeondata = character_data_raider_io["mythic_plus_best_runs"]
        #hier werden die raider IO daten aufbereitet
        list_with_raid_names = list(character_data_raider_io["raid_progression"].keys())
        summaries = [character_data_raider_io["raid_progression"][key]['summary'] for key in list_with_raid_names]
        df_with_raid_names = pd.DataFrame({'name': list_with_raid_names, 'summary': summaries})

        # hier werden die in der datenbank hinterlegten daten aufbereitet - es wird der aktuellste eintrag hergenommen
        # if schleife um zu schauen, ob bei raider io ein neuer eintrag da ist, der in der DB noch nicht ist
        # falls ident, wird der aktuellste aus der DB genommen und darauf wird gefiltert
        # falls nicht ident, wird geschaut was bei Raider IO neu ist und das wird als name herangezogen
        # ausserdem wird das neue dann mit dem heutigen datum in die DB gepushed
        raider_io_raidnames = set(list_with_raid_names)
        db_raidnames = set(list_with_db_raid_names)
        if raider_io_raidnames == db_raidnames:
            latest_raid_tier = raid_release_dates_df.loc[raid_release_dates_df["first_seen"].idxmax()]
            latest_raid_tier_name = latest_raid_tier["name"]
        else:
            latest_raid_tier_name = list(raider_io_raidnames.symmetric_difference(db_raidnames))[0] #hier wird geschaut welche entries bei Raider.io vorhanden sind, in der DB aber noch nicht
            connection_obj = sqlite3.connect("/home/paulherzog/sql_databases/jack_wow.db")
            cursor_obj = connection_obj.cursor()
            print("Connected to jack_wow.db for updating raid tier name.")
            new_raid_data = (latest_raid_tier_name, datetime.now().strftime("%d-%m-%Y"))
            cursor_obj.execute("INSERT INTO raid_names (name, first_seen) VALUES (?, ?)", new_raid_data)
            connection_obj.commit()
            connection_obj.close()

        character_data["raid_summary"] = df_with_raid_names[df_with_raid_names['name'] == latest_raid_tier_name]['summary'].values[0]
        # looping through dungeon data and initialize variables for sqlite database

        for i, dungeon_data in enumerate(character_data_raider_io["mythic_plus_best_runs"], start=1):
            dungeon_name_long = dungeon_data.get("dungeon", "")
            character_data[f'dungeon_{i}_name_long'] = dungeon_name_long


            dungeon_name_short = dungeon_data.get("short_name", "")
            character_data[f'dungeon_{i}_name_short'] = dungeon_name_short


            dungeon_mythic_level = dungeon_data.get("mythic_level", "")
            character_data[f'dungeon_{i}_mythic_level'] = dungeon_mythic_level


            dungeon_date = dungeon_data.get("completed_at", "")
            if dungeon_date:
                dungeon_date = datetime.strptime(dungeon_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y")
            character_data[f'dungeon_{i}_date'] = dungeon_date


            dungeon_cleartime = dungeon_data.get("clear_time_ms", "")
            if dungeon_cleartime:
                minutes, seconds = divmod(dungeon_cleartime // 1000, 60)
                dungeon_cleartime = f"{minutes:02}:{seconds:02}"
            character_data[f'dungeon_{i}_cleartime'] = dungeon_cleartime


            dungeon_keystone_upgrades = dungeon_data.get("num_keystone_upgrades", "")
            character_data[f'dungeon_{i}_keystone_upgrades'] = dungeon_keystone_upgrades


            dungeon_bestrun_url = dungeon_data.get("url", "")
            character_data[f'dungeon_{i}_bestrun_url'] = dungeon_bestrun_url
        #append char data
        current_date = datetime.now()
        timestamp_api_fetch = current_date.strftime("%d-%m-%Y")

        character_data["date_data_fetched"] = timestamp_api_fetch
        character_data_list.append(character_data)
df_character_data = pd.DataFrame(character_data_list)
# Assuming you have a Pandas DataFrame named 'df'
# Create a connection to the SQLite database
connection_obj = sqlite3.connect('/home/paulherzog/sql_databases/jack_wow.db') 
print("Connection to jack_wow.db.")
# Use the to_sql method to write the DataFrame to the database
df_character_data.to_sql('char_performance_data', connection_obj, if_exists='replace', index=False)  # 'replace' will replace the table if it already exists
print("Character Data pushed to table 'char_performance_data'")
#now check what the current raid is
#raid_release_dates_statement = """SELECT name, first_seen FROM raid_names; """
#cursor_obj.execute(raid_release_dates_statement)
#raid_release_dates_db_data = cursor_obj.fetchall()
#raid_release_dates_df = pd.DataFrame(columns["name", "first_seen"]
#for row in raid_release_dates_db_data:
#      raid_release_dates_df = raid_release_dates_df.append({"name":row	[0], "first_seen": row[1]}, ignore_index=True)
#print("Successfully fetched Raid Names & Release Dates from DB")
#print(raid_release_dates_df)
# Close the database connection
connection_obj.close()
