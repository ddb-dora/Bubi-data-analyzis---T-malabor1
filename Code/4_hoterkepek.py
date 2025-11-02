import folium
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def station_traffic(data):
    start_counts = data.groupby(['start_place_id', 'start_lat', 'start_lng']).size().reset_index(name='count')
    start_counts.rename(columns={'start_place_id': 'station_id', 'start_lat': 'lat', 'start_lng': 'lng'}, inplace=True)

    end_counts = data.groupby(['end_place_id', 'end_lat', 'end_lng']).size().reset_index(name='count')
    end_counts.rename(columns={'end_place_id': 'station_id', 'end_lat': 'lat', 'end_lng': 'lng'}, inplace=True)

    traffic = pd.concat([start_counts, end_counts])
    traffic = (
        traffic.groupby('station_id')
        .agg({'count': 'sum', 'lat': 'mean', 'lng': 'mean'})
        .reset_index()
    )
    return traffic


def color_by_traffic(count, cmap, min_count, max_count):
    norm = mcolors.Normalize(vmin=min_count, vmax=max_count)
    rgb = cmap(norm(count))[:3]
    return mcolors.to_hex(rgb)


def generate_maps(stations, open_date_str, filename_prefix, df):
    open_date = pd.to_datetime(open_date_str)
    
    before_period = (df['start_time'] >= open_date - pd.Timedelta(days=90)) & (df['start_time'] < open_date)
    after_period = (df['start_time'] >= open_date) & (df['start_time'] < open_date + pd.Timedelta(days=90))

    before_traffic = station_traffic(df[before_period])
    after_traffic = station_traffic(df[after_period])

    warm_colormap = cm.get_cmap('YlOrRd')   
    cool_colormap = cm.get_cmap('winter')   
    min_count = min(before_traffic['count'].min(), after_traffic['count'].min())
    max_count = max(before_traffic['count'].max(), after_traffic['count'].max())

    coords = df[df['end_place_id'].isin(stations)][['end_lat', 'end_lng']].dropna()
    center_lat = coords['end_lat'].mean()
    center_lng = coords['end_lng'].mean()

    m_before = folium.Map(location=[center_lat, center_lng], zoom_start=13, tiles="CartoDB positron")
    for _, row in before_traffic.iterrows():
        color = color_by_traffic(row['count'], warm_colormap, min_count, max_count)
        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=2 + row['count'] / 500,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"{row['station_id']}: {row['count']} trips (before)"
        ).add_to(m_before)
    m_before.save(f"{filename_prefix}_before_traffic.html")

    m_after = folium.Map(location=[center_lat, center_lng], zoom_start=13, tiles="CartoDB positron")
    for _, row in after_traffic.iterrows():
        if row['station_id'] in stations:
            color = color_by_traffic(row['count'], cool_colormap, min_count, max_count)
        else:
            color = color_by_traffic(row['count'], warm_colormap, min_count, max_count)
        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=2 + row['count'] / 500,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"{row['station_id']}: {row['count']} trips (after)"
        ).add_to(m_after)
    m_after.save(f"{filename_prefix}_after_traffic.html")

    print(f"✅ Maps saved for {filename_prefix}:")
    print(f"  • {filename_prefix}_before_traffic.html")
    print(f"  • {filename_prefix}_after_traffic.html\n")


generate_maps(
    stations=["1406-Egressy út - Stefánia út", "1407-Stefánia út - Thököly út",
              "1408-Zugló vasútállomás", "1409-Kacsóh Pongrác út",
              "1410-Papp László Budapest Sportaréna", "1411-Reiner Frigyes park"],
    open_date_str="2023-06-28",
    filename_prefix="zuglo",
    df=df
)

generate_maps(
    stations=["0921-Mester utca - Ferenc körút", "0922-Haller utca – Mester utca",
              "0923-Nádasdy utca (játszótér)", "0924-Haller utca - Soroksári út"],
    open_date_str="2023-09-01",
    filename_prefix="kerulet9",
    df=df
)

generate_maps(
    stations=["1137-Kopaszi-gát"],
    open_date_str="2024-04-09",
    filename_prefix="kopaszi",
    df=df
)

generate_maps(
    stations=["0620-Westend - Balzac utca"],
    open_date_str="2024-05-01",
    filename_prefix="westend",
    df=df
)

generate_maps(
    stations=["1128-Csonka János tér"],
    open_date_str="2022-06-15",
    filename_prefix="csonka",
    df=df
)
