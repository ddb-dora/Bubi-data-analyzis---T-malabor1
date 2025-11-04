import folium
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

# Loading the data file of the stations
def data_file_of_all_stations_loader():
    df = pd.read_excel("Bubi_stations_final.xlsx")
    df["Üzembe helyezés dátuma"] = pd.to_datetime(df["Üzembe helyezés dátuma"], errors="coerce")
    return df

# Defining a function to assign colors based on the opening date
def get_color(date):
    if date.year == 2014:
            return "green"
    elif date.year == 2025:
        return "purple"
    elif date.year == 2024:
        return "gray"
    elif (date.year == 2023) and (date.month in [1,2,3]):
        return "red"
    elif (date.year == 2023) and (date.month in [6,7,8,9]):
        return "orange"
    elif (date.year == 2022) and (date.month in [4,5]):
        return "blue"
    elif date.year == 2022 and date.month in [6,7]:
        return "cadetblue"
    elif (date.year == 2022) and (date.month in [11,12]):
        return "lightblue"
    else:
        return "black"

# Create a map centered around the average coordinates
def map_creator(data_file):
    m = folium.Map(location=[data_file["Lat"].mean(), data_file["Long"].mean()], zoom_start=12)
    return m


# Add points for each station
def point_adder_to_stations(data_file, map):
    for _, row in data_file.iterrows():
        colorOfStation = get_color(row["Üzembe helyezés dátuma"])
        folium.Marker(
            location=[row["Lat"], row["Long"]],
            popup=row["Gyűjtőállomás neve"],
            icon=folium.Icon(color=colorOfStation, icon="info-sign"),
        ).add_to(map)

    # Save the map as an HTML file
    map.save("stations_map.html")

    print("✅ Map saved as stations_map.html. Open it in your browser to view it!")

selected_keys = [
    "1131-Kelenföld vasútállomás M (Etele tér)",
    "1124 - Vahot utca - Wartha Vince utca",
    "1125-Bikás park M",
    "1130-Hauszmann Alajos utca - Fehérvári út",
    "1126-Szent Imre Kórház",
    "1122-Szent Gellért-templom",
    "1127-Fraknó utca - Bánk Bán utca",
    "1123-Karolina út - Tétényi út",
    "1121-Csóka utca - Bogyó utca",

    "0310-Kiscelli utca - Pacsirtamező utca",
    "0309-Tímár utca H",
    "0311-Kórház utca - Polgár utca",
    "0307-Szentlélek tér H",
    "0312-Szőlő utca - Vörösvári út",
    "0308-Flórián tér",
    "0313-Óbudai rendelőintézet",

    "1407-Stefánia út - Thököly út",
    "1411-Reiner Frigyes park",
    "1408-Zugló vasútállomás",
    "1405-Zichy Géza utca – Ajtósi Dürer sor",
    "1404-Olof Palme sétány - Dvořák sétány",
    "1403-Városligeti Műjégpálya és Csónakázótó",
    "1409-Kacsóh Pongrác út"
]

"""
Creates an interactive map (HTML) showing total station traffic (start + end rides)
for a given year using all available stations.
"""
# What has changed in one year
def generate_traffic_map(year, data_file):
    df = pd.read_parquet(data_file)

    # Filter for selected year
    df = df[df["year"] == year]
    print(f"📅 Year {year}: {len(df):,} trips")

    if df.empty:
        print("⚠️ No trips found for this year.")
        return

    # Count total traffic (start + end) per station
    starts = (
        df.groupby(["start_place_id", "start_lat", "start_lng"])
        .size()
        .reset_index(name="rides")
    )
    ends = (
        df.groupby(["end_place_id", "end_lat", "end_lng"])
        .size()
        .reset_index(name="rides")
    )

    # Align column names for merging
    starts = starts.rename(columns={
        "start_place_id": "place_id",
        "start_lat": "lat",
        "start_lng": "lng"
    })
    ends = ends.rename(columns={
        "end_place_id": "place_id",
        "end_lat": "lat",
        "end_lng": "lng"
    })

    # Merge start + end rides
    station_stats = pd.concat([starts, ends], ignore_index=True)
    station_stats = (
        station_stats.groupby(["place_id", "lat", "lng"])["rides"]
        .sum()
        .reset_index()
    )

    print(f"📊 {len(station_stats)} stations found.")

    # Create map centered on the data
    center_lat = station_stats["lat"].mean()
    center_lng = station_stats["lng"].mean()
    m = folium.Map(location=[center_lat, center_lng], zoom_start=12)

    # save numerical data too
    radiuses = {}

    # Add circle markers
    max_rides = station_stats["rides"].max()
    for _, row in station_stats.iterrows():
        radius = max(3, (row["rides"] / max_rides) * 30)  # Scale size 3–30
        radiuses[row["place_id"]] = round(radius, 2)      # generating a dictionary with the places name and the radius size,
                                                          # We used it for comparing
        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=radius,
            color="green",
            fill=True,
            fill_opacity=0.6,
            popup=f"Station: {row['place_id']}<br>Total rides: {row['rides']}",
        ).add_to(m)

    for key in selected_keys:
        with open('Choosen_stations_radiuses.txt', 'w') as file:
            if key in radiuses:
                print(key, "\t", radiuses[key], "\n")
            else:
                print(key, "\t⚠️ not found")

    # Save map
    output_file = f"traffic_map_{year}.html"
    m.save(output_file)
    print(f"✅ Map saved: {output_file}")

# yearly change in the number of users
def yearly_change_in_number_of_riders(df):
    # Exclude 2025
    yearly = df[df["year"] != 2025].groupby("year").size()

    # Create figure
    plt.figure(figsize=(8,5))
    plt.plot(yearly.index, yearly.values, marker="o", color="teal")
    plt.title("Total Bubi Rides per Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Rides (millions)")
    plt.grid(True)

    # Format Y-axis
    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(100000))                         # step of 500k
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))  # show in millions

    plt.tight_layout()
    plt.savefig("bubi_riders_per_year.png", dpi=300)
    print("✅ Graph saved as bubi_riders_per_year.png")



