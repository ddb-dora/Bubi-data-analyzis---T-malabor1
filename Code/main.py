import pandas as pd
import folium
import a_egyesites
import b_alapstatisztikak
import c_felhasznalok_aktivitasa
import d_hoterkepek
import e_map

"""At the very first time:
    1. Uncomment the "a_egyesites.create_database()" line
    2. Run the code
    3. Make the "a_egyesites.create_database()" line to be a comment again
    After doing this once on your computer, you should only do this again 
    if someone has changed the data files which the code reading from for 
    the mentionned function in the file "a_egyesites". 
    This line builds up the data base, but it runs for a quite long time.
    The next line only use that generated file, which does not take long at all.
"""
# Data reading from excel
#a_egyesites.create_database()
df = pd.read_parquet("merged_data.parquet") # df here is not actually data file, it is the already read data
##############################################################################################

# Saving statistical calculations' result
b_alapstatisztikak.statistical_result_to_file(df)
b_alapstatisztikak.busiest_stations_data_to_file(df)
b_alapstatisztikak.traffic_of_stations_to_map(df)
##############################################################################################

# figures about user activity
res_df = c_felhasznalok_aktivitasa.user_activity_calculator(df)
c_felhasznalok_aktivitasa.share_of_users_by_station_group_figure_generator(res_df)
c_felhasznalok_aktivitasa.figure_generator_about_user_number_in_90_days(res_df)
##############################################################################################

#
d_hoterkepek.generate_maps(
    stations=["1406-Egressy út - Stefánia út", "1407-Stefánia út - Thököly út",
              "1408-Zugló vasútállomás", "1409-Kacsóh Pongrác út",
              "1410-Papp László Budapest Sportaréna", "1411-Reiner Frigyes park"],
    open_date_str="2023-06-28",
    filename_prefix="zuglo",
    df=df
)

d_hoterkepek.generate_maps(
    stations=["0921-Mester utca - Ferenc körút", "0922-Haller utca – Mester utca",
              "0923-Nádasdy utca (játszótér)", "0924-Haller utca - Soroksári út"],
    open_date_str="2023-09-01",
    filename_prefix="kerulet9",
    df=df
)

d_hoterkepek.generate_maps(
    stations=["1137-Kopaszi-gát"],
    open_date_str="2024-04-09",
    filename_prefix="kopaszi",
    df=df
)

d_hoterkepek.generate_maps(
    stations=["0620-Westend - Balzac utca"],
    open_date_str="2024-05-01",
    filename_prefix="westend",
    df=df
)

d_hoterkepek.generate_maps(
    stations=["1128-Csonka János tér"],
    open_date_str="2022-06-15",
    filename_prefix="csonka",
    df=df
)
##############################################################################################

# Map generation about the stations
df_stations = e_map.data_file_of_all_stations_loader() # data file reading which only contains the stations
e_map.point_adder_to_stations(df_stations, e_map.map_creator(df_stations))

# Map about yearly traffic
e_map.generate_traffic_map(2022, "merged_data.parquet")
e_map.generate_traffic_map(2023, "merged_data.parquet")
e_map.generate_traffic_map(2024, "merged_data.parquet")
e_map.generate_traffic_map(2025, "merged_data.parquet")

# What has changed in one year
e_map.yearly_change_in_number_of_riders(df)
##############################################################################################
