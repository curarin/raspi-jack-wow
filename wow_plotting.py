import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
from PIL import Image, ImageEnhance
import os

### GET DB DATA ###
connection_obj = sqlite3.connect("/home/paulherzog/sql_databases/jack_wow.db")
table_name_char_data = "char_performance_data"
cursor_obj = connection_obj.cursor()
print("Connected to jack_wow.db.")
schema_info = cursor_obj.fetchall()

query = f"SELECT * FROM {table_name_char_data}"
df_with_api_data = pd.read_sql_query(query, connection_obj)
connection_obj.close()

## FUNCTION FOR JPG TO BMP
def img_convert(img_file,X_new,Y_new):
        img = Image.open(img_file)
        enhancer = ImageEnhance.Contrast(img)
        contrast = 5
        img = enhancer.enhance(contrast)
        img = img.convert("1")
        img = img.resize((X_new,Y_new), Image.LANCZOS)
        return img


def custom_convert(value):
        try:
           return float(value)
        except ValueError:
           return 0

########

### LOOPING ###
for char in df_with_api_data.itertuples(index=False):
        char_name = char.charname
        row_data_currently_selected = df_with_api_data[df_with_api_data["charname"] == char_name]
        kills_data = row_data_currently_selected.filter(like='_totalkills')
        encounter_numbers = df_with_api_data.filter(like='_totalkills')
        encounter_count = len(encounter_numbers.columns)
        rank_percent_data = row_data_currently_selected.filter(like='_rankpercent')
        region_rank_data = row_data_currently_selected.filter(like='_regionrank')
 #       rank_percent_data = rank_percent_data.replace('None', 0).astype(float)
        rank_percent_data = rank_percent_data.applymap(custom_convert).astype(float)
        encounter_names = [df_with_api_data[f'encounter_{i}_name'].iloc[0] for i in range(1, encounter_count + 1)]

        region_ranks = [region_rank_data[f'encounter_{i}_regionrank'] for i in range(1, encounter_count + 1)]

        x = np.arange(encounter_count)

        bar_width = 0.45
        print(f"Plotting starts for {char_name}...")
        fig, ax1 = plt.subplots(figsize=(10, 6))
        bars1 = ax1.bar(x, kills_data.iloc[0], width=bar_width, label='Total Kills', color='lightgray',hatch='////')  # Gray hatch pattern

        ax1.set_xticks(x + bar_width)
        encounter_names_split = ['\n'.join(name.split(' ', len(name) // 2)) for name in encounter_names]
        ax1.set_xticklabels(encounter_names_split, rotation=45, ha="right", fontsize=10)

        ax1.set_xlabel('Encounters')
        ax1.set_ylabel('Total Kills')
        ax1.set_title('Raid Performance Overview')
#        ax1.legend(loc='upper left')

        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + bar_width, rank_percent_data.iloc[0], width=bar_width, label='Top Ranking Percentile (in %)',color='black', hatch='\\\\\\\\')  # Black hatch pattern
#        for bar in bars2:
#                bar.set_linewidth(1.0)
        ax2.set_ylabel('Top Ranking Percentile (in %)')
#        ax2.legend(loc='upper right')

        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        for bar1, bar2, encounter_name in zip(bars1, bars2, encounter_names):
                height1 = bar1.get_height()
                height2 = bar2.get_height()
                ax1.annotate(f'{height1}', (bar1.get_x() + bar1.get_width() / 2, height1),
                         ha='center', va='bottom', fontsize=10)
                ax2.annotate(f'{height2:.2f}', (bar2.get_x() + bar2.get_width() / 2, height2),
                        ha='center', va='bottom', fontsize=10)
                region_rank = region_ranks[encounter_names.index(encounter_name)]
                try:
                        region_rank = int(region_rank)
                except ValueError:
                        region_rank = 0
                if (region_rank == 1):
                        bar_middle_x = bar2.get_x() + bar2.get_width() / 2
                        star_y = height2 * 0.7
                        ax2.annotate("""
 .__.
 (|  |)
 (  )
 _)(_ 
 R
 1

 G
 G
 W
 P

""",(bar_middle_x, star_y), ha='center', va='center', fontsize=10, color='white')
                if (region_rank <= 3) & (region_rank > 1):
                        bar_middle_x = bar2.get_x() + bar2.get_width() / 2
                        star_y = height2 * 0.5
                        ax2.annotate("""
 .__.
 (|  |)
 (  )
 _)(_ 
TOP
 3



""", (bar_middle_x, star_y), ha='center', va='center', fontsize=10, color='white')
                if (region_rank > 3) & (region_rank <= 10):
                        bar_middle_x = bar2.get_x() + bar2.get_width() / 2
                        star_y = height2 * 0.5  # Adjust the y-coordinate to 50% of the bar's height
                        ax2.annotate("""
 .__.
 (|  |)
 (  )
 _)(_ 
TOP
10

""", (bar_middle_x, star_y), ha='center', va='center', fontsize=10, color='white')
                elif (region_rank < 50) & (region_rank > 10):
                        # Calculate the middle position of the bar and adjust the y-coordinate for the star
                        bar_middle_x = bar2.get_x() + bar2.get_width() / 2
                        star_y = height2 * 0.2  # Adjust the y-coordinate to 50% of the bar's height
                        ax2.annotate("""
 .__.
 (|  |)
 (  )
 _)(_
TOP
50

""", (bar_middle_x, star_y), ha='center', va='center', fontsize=10, color='white')

 #       ax1.legend(loc='upper left', bbox_to_anchor=(0.05, 1.0))
 #       ax2.legend(loc='upper left', bbox_to_anchor=(0.4, 1.0))

        plt.tight_layout()
        dpi = 240
        temp_file = f'/home/paulherzog/python/raid_overview_{char_name}.png'
        plt.savefig(temp_file, dpi=dpi, bbox_inches='tight', transparent=True)
        #bmp_image = img_convert(temp_file, 800, 400)
        bmp_image = Image.open(temp_file)
        bmp_file = f'raid_overview_{char_name}.bmp'
        bmp_image.save(bmp_file, dpi=(dpi, dpi))
        os.remove(temp_file)
        print(f"Raid Data Plotting completed for {char_name}...")
