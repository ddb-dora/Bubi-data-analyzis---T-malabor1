import matplotlib.pyplot as plt
import pandas as pd
import folium

# Statisztikák
def statistical_result_to_file(df):
    # Open a file in write mode (this will overwrite the file if it exists)
    with open('statistical_results.txt', 'w') as file:
        print("Utazások száma:", len(df))
        print("Átlagos utazási idő (perc):", df['duration_min'].mean().round(2))
        print("Medián utazási idő (perc):", df['duration_min'].median().round(2))

        df['hour'] = df['start_time'].dt.hour
        traffic_by_hour = df.groupby('hour').size()
        print("\nÓránkénti utazások száma:")
        print(traffic_by_hour)

        df['month'] = df['start_time'].dt.month
        traffic_by_month = df.groupby(['year', 'month']).size()
        print("\nHónaponkénti utazások száma (évenként):")
        print(traffic_by_month)

#Legforgalmasabb állomások:
def busiest_stations_data_to_file(df):
    start_counts = df.groupby('start_place_id').size().reset_index(name='indulások')
    end_counts = df.groupby('end_place_id').size().reset_index(name='érkezések')

    station_traffic = pd.merge(start_counts, end_counts,
                           left_on='start_place_id', right_on='end_place_id',
                           how='outer')

    station_traffic['állomás'] = station_traffic['start_place_id'].combine_first(station_traffic['end_place_id'])
    station_traffic['összes_forgalom'] = station_traffic['indulások'].fillna(0) + station_traffic['érkezések'].fillna(0)

    top_stations = station_traffic.sort_values('összes_forgalom', ascending=False).head(10)

    with open('statistical_results.txt', 'a') as file:  # 'a' = append mode
        print(top_stations[['állomás', 'összes_forgalom']])

# Bérlettípusok aránya évenként
def prices_of_passes_to_chart(df):
    license_share = df.groupby(['year', 'coupon_name']).size().reset_index(name='trips')
    license_share['share (%)'] = (
        license_share['trips'] /
        license_share.groupby('year')['trips'].transform('sum') * 100
    ).round(2)


    name_map = {
        'Havi bérlet': 'Monthly Pass',
        'Éves bérlet': 'Annual Pass',
        'PAYG': 'Pay As You Go'
    }
    license_share['coupon_name'] = license_share['coupon_name'].replace(name_map)

    top3 = (
        license_share.groupby('coupon_name')['trips']
        .sum()
        .nlargest(3)
        .index
    )
    top3_df = license_share[license_share['coupon_name'].isin(top3)]

    plt.figure(figsize=(9, 5))
    colors = {
        'Pay As You Go': '#1f77b4',
        'Monthly Pass': '#ff7f0e',
        'Annual Pass': '#2ca02c'
    }

    for name in top3_df['coupon_name'].unique():
        subset = top3_df[top3_df['coupon_name'] == name]
        plt.plot(subset['year'], subset['share (%)'], marker='o', label=name, color=colors.get(name))

    plt.title("Change in Pass Type Share (2022–2024)")
    plt.xlabel("Year")
    plt.ylabel("Share (%)")
    plt.legend(title="Pass Type")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    plt.savefig('prices of passes')

#Állomások forgalma
def traffic_of_stations_to_map(df):
    station_coords = df.groupby('start_place_id')[['start_lat', 'start_lng']].mean().reset_index()
    station_coords.rename(columns={'start_place_id': 'állomás'}, inplace=True)

    start_counts = df.groupby('start_place_id').size().reset_index(name='indulások')
    end_counts = df.groupby('end_place_id').size().reset_index(name='érkezések')

    station_traffic = pd.merge(start_counts, end_counts,
                               left_on='start_place_id', right_on='end_place_id',
                               how='outer')

    station_traffic['állomás'] = station_traffic['start_place_id'].combine_first(station_traffic['end_place_id'])
    station_traffic['összes_forgalom'] = station_traffic['indulások'].fillna(0) + station_traffic['érkezések'].fillna(0)

    station_map_data = pd.merge(station_coords, station_traffic, on='állomás', how='left')

    m = folium.Map(location=[47.4979, 19.0402], zoom_start=12)

    for _, row in station_map_data.iterrows():
        folium.CircleMarker(
            location=[row['start_lat'], row['start_lng']],
            radius=row['összes_forgalom'] / 100000,
            color='blue',
            fill=True,
            fill_opacity=0.5,
            popup=f"{row['állomás']} – {int(row['összes_forgalom'])} utazás"
        ).add_to(m)

    m.save("bubi_allomasok_forgalma.html")