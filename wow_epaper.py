import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import sys
import epaper
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import sqlite3
import os
import gpiozero
from signal import pause
import requests
from io import BytesIO


##### DRIVERS AND INITIALIZING DISPLAY########
epd = epaper.epaper("epd7in5_V2").EPD() # get the display
epd.init()           # initialize the display
print("Clearing display...")    # prints to console, not the display, for debugging
epd.Clear()      # clear the display

### DEFINING BUTTONS
key1 = gpiozero.Button(3)
key2 = gpiozero.Button(4)

##### FONTS #######
font_content = ImageFont.truetype("/home/paulherzog/.fonts/folkard_.ttf", 25)  #folkard
font_header = ImageFont.truetype("/home/paulherzog/.fonts/LifeCraft_Font.ttf", 60) #lifecraft

### GET DB DATA ###
connection_obj = sqlite3.connect("/home/paulherzog/sql_databases/jack_wow.db")
table_name_char_data = "char_performance_data"
cursor_obj = connection_obj.cursor()
print("Connected to jack_wow.db.")
schema_info = cursor_obj.fetchall()

query = f"SELECT * FROM {table_name_char_data}"
df_with_api_data = pd.read_sql_query(query, connection_obj)
connection_obj.close()
number_of_rows_in_df = len(df_with_api_data)
current_row_selected = 0

### DEFINING FUNCTIONS
## for button action ###
def button_a_callback():
	global current_row_selected
	current_row_selected = (current_row_selected + 1) % number_of_rows_in_df
	data_current_row()

def button_b_callback():
	global current_row_selected
	current_row_selected = (current_row_selected - 1) % number_of_rows_in_df
	data_current_row()

key1.when_pressed = button_a_callback
key2.when_pressed = button_b_callback

# for defining which class thumbnail to get
def get_class_picture(char_class):
	path = "/home/paulherzog/python/"
	if char_class == "Warrior":
		class_picture = "classicon_warrior.bmp"
	elif char_class == "Druid":
		class_picture = "classicon_druid.bmp"
	elif char_class == "Warlock":
		class_picture = "classicon_warlock.bmp"
	elif char_class == "Monk":
		class_picture = "classicon_monk.bmp"
	elif char_class == "Shaman":
		class_picture = "classicon_shaman.bmp"
	elif char_class == "Paladin":
		class_picture = "classicon_paladin.bmp"
	elif char_class == "Evoker":
		class_picture = "classicon_evoker.bmp"
	elif char_class == "Demon Hunter":
		class_picture = "classicon_demon_hunter.bmp"
	elif char_class == "Death Knight":
		class_picture = "classicon_death_knight.bmp"
	elif char_class == "Mage":
		class_picture = "classicon_mage.bmp"
	elif char_class == "Rogue":
		class_picture = "classicon_rogue.bmp"
	elif char_class == "Priest":
		class_picture = "classicon_priest.bmp"
	elif char_class == "Hunter":
		class_picture = "classicon_hunter.bmp"
	else:
		class_picture = "classicon_monk.bmp"
	path_to_classicon = path + class_picture
	return path_to_classicon

# for getting plot data
def get_raid_plot(char_name):
	path = "/home/paulherzog/python/"
	file_name = f"raid_overview_{char_name}.bmp"
	full_path_to_plot = path + file_name
	return full_path_to_plot

## for storing data based on current button selection and pushing to epaper
def data_current_row():
	row_data_currently_selected = df_with_api_data.iloc[current_row_selected]
	HImage = Image.new("1", (epd.width, epd.height), 255)
	draw = ImageDraw.Draw(HImage)

	#character data
	char_name = row_data_currently_selected["charname"]
	char_class = row_data_currently_selected["charclass"]
	char_realm = row_data_currently_selected["charrealm"]
	char_guild = row_data_currently_selected["charguild"]
	char_realm = row_data_currently_selected["charrealm"]
	char_ilevel = row_data_currently_selected["charilevel"]
	char_rio = row_data_currently_selected["mplus_rio"]
	char_wcl_performance_average = row_data_currently_selected["wcl_performance_average"]
	raid_summ = row_data_currently_selected["raid_summary"]

	#picture data
	class_picture_bmp = get_class_picture(char_class)
	img_bmp = Image.open(class_picture_bmp)
	class_picture_bmp = img_bmp
	HImage.paste(class_picture_bmp, (5, 5))

	#misc data
	date_last_api_fetch = row_data_currently_selected["date_data_fetched"]
	print(f"Data for Character '{char_name}' in Row:", current_row_selected)

	#here we are pushing all relevent informations #
	draw.text((60, 5), char_name, font = font_header, fill = 0)
	draw.text((300, 10), char_realm, font = font_content, fill = 0)
	draw.text((300, 40), char_guild, font = font_content, fill = 0)
	draw.text((460, 10), f"iLevel: {char_ilevel}", font = font_content, fill = 0)
	draw.text((460, 40), f"RIO: {char_rio}", font = font_content, fill = 0)
	draw.text((640, 10), f"Raid: {raid_summ}", font = font_content, fill = 0)
	draw.text((640, 40), f"WCL:  {char_wcl_performance_average}", font = font_content, fill = 0)
	#draw.text((600, 0), "Last Update: " + date_last_api_fetch, fill = 0)
	#draw.text((600, 40), f"Character {current_row_selected}/{number_of_rows_in_df}", fill = 0)

        #draw lines
	draw.line([(5,70),(795,70)], fill = 0, width = 1)

	#push plots
	raid_plot_bmp = get_raid_plot(char_name)
	raid_plot_bmp = Image.open(raid_plot_bmp)
	raid_plot_bmp = raid_plot_bmp.resize((800, 400), Image.ANTIALIAS)
	HImage.paste(raid_plot_bmp, (0, 80))

	#push to display
	epd.display(epd.getbuffer(HImage))
	time.sleep(2)
#################### GET ALL THE DATA FROM DATAFRAME

######## PUSH FIRST VEW AFTER REBOOT
data_current_row()

###################################################
try:
	pause()

except KeyboardInterrupt:
	pass



