import pandas as pd
import folium
from datetime import datetime
# Generating code for representing the Bubi stations in Budapest

# Loading the data file of the stations
df = pd.read_excel("Bubi_stations_2023_05.xlsx")
df["Üzembe helyezés dátuma"] = pd.to_datetime(df["Üzembe helyezés dátuma"], errors="coerce")

# Defineing a function to assign colors based on the opening date
def get_color(date):
    if date.year == 2014:
            return "green"
    elif (date.year == 2023) and (date.month in [1,2,3]):
        return "red"
    elif (date.year == 2022) and (date.month in [4,5]):
        return "blue"
    elif date.year == 2022 and date.month in [6,7]:
        return "cadetblue"
    elif (date.year == 2022) and (date.month in [11,12]):
        return "lightblue"
    else:
        return "gray"

# Create a map centered around the average coordinates
m = folium.Map(location=[df["Lat"].mean(), df["Long"].mean()], zoom_start=12)


# Add points for each station
for _, row in df.iterrows():
    colorOfStation = get_color(row["Üzembe helyezés dátuma"])
    folium.Marker(
        location=[row["Lat"], row["Long"]],
        popup=row["Gyűjtőállomás neve"],
        icon=folium.Icon(color=colorOfStation, icon="info-sign")
    ).add_to(m)

# Save the map as an HTML file
m.save("stations_map.html")

print("✅ Map saved as stations_map.html. Open it in your browser to view it!")
