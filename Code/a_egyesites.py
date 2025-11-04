import pandas as pd
import glob
import os

base_folder = r"Adatok"
years = ["2022", "2023", "2024", "2025"]

dfs = []
pattern = r'^\d{4}-'
"""
This function goes through on each year's data and put it into one data file.
It also sorts out the routes which were shorter than 1 minute, 
and also the lines which contain incorrect data 
"""
def create_database():
    for year in years:
        folder_path = os.path.join(base_folder, year)
        file_list = glob.glob(os.path.join(folder_path, "*.xlsx"))
        print(f"{year}: {len(file_list)} fájl található")

        for file in file_list:
            print("Beolvasás:", file)
            temp_df = pd.read_excel(file)
            temp_df["year"] = int(year)

            mask = (
                temp_df['start_place_id'].astype(str).str.match(pattern) &
                temp_df['end_place_id'].astype(str).str.match(pattern)
            )
            temp_df = temp_df[mask]

            cols = ['start_time', 'end_time', 'duration', 'start_place_id', 'end_place_id',
                    'start_lat', 'start_lng', 'end_lat', 'end_lng',
                    'cust_id', 'bike_id', 'coupon_name', 'year']
            temp_df = temp_df[cols]

            dfs.append(temp_df)

    #Összefűzés
    df = pd.concat(dfs, ignore_index=True)
    print("Összes sor beolvasva és szűrve:", len(df))

    #Dátumkonverziós
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
    df = df.dropna(subset=['start_time', 'end_time'])

    #Időtartam percben
    df['duration_min'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    df = df[(df['duration_min'] > 0) & (df['duration_min'] < 120)]

    #Adatok mentése egyetlen fájlba, hogy a későbbi futtatásokat rövidítsük
    output_file = "merged_data.parquet"
    df.to_parquet(output_file, index=False)
    print(f"Saved combined data to {output_file}")