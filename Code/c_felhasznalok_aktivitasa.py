import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

station_groups = [
    {
        "name": "Csonka János Square",
        "station_ids": ["1128-Csonka János tér"],
        "open": "2022-06-15"
    },
    {
        "name": "Zugló Group",
        "station_ids": [
            "1406-Egressy út - Stefánia út",
            "1407-Stefánia út - Thököly út",
            "1408-Zugló vasútállomás",
            "1409-Kacsóh Pongrác út",
            "1410-Papp László Budapest Sportaréna",
            "1411-Reiner Frigyes park"
        ],
        "open": "2023-06-28"
    },
    {
        "name": "District 9 Stations",
        "station_ids": [
            "0921-Mester utca - Ferenc körút",
            "0922-Haller utca – Mester utca",
            "0923-Nádasdy utca (játszótér)",
            "0924-Haller utca - Soroksári út"
        ],
        "open": "2023-09-01"
    },
    {
        "name": "Kopaszi-gát",
        "station_ids": ["1137-Kopaszi-gát"],
        "open": "2024-04-09"
    },
    {
        "name": "Westend – Balzac Street",
        "station_ids": ["0620-Westend - Balzac utca"],
        "open": "2024-05-01"
    }
]

results = []
def user_activity_calculator(df):
    for group in station_groups:
        group_name = group["name"]
        station_ids = group["station_ids"]
        open_date = pd.to_datetime(group["open"])

        before_start = open_date - pd.Timedelta(days=90)
        after_end = open_date + pd.Timedelta(days=90)

        users_after_group = set(
            df[
                ((df['start_place_id'].isin(station_ids)) | (df['end_place_id'].isin(station_ids))) &
                (df['start_time'].between(open_date, after_end))
            ]['cust_id']
        )

        users_before_system = set(
            df[
                df['start_time'].between(before_start, open_date)
            ]['cust_id']
        )

        new_users = users_after_group - users_before_system
        migrated_users = users_after_group & users_before_system

        total_after = len(users_after_group)
        new_ratio = (len(new_users) / total_after * 100) if total_after > 0 else 0
        migrated_ratio = (len(migrated_users) / total_after * 100) if total_after > 0 else 0

        results.append({
            "Station Group": group_name,
            "Opening Date": group["open"],
            "New Users": len(new_users),
            "Migrated Users": len(migrated_users),
            "Total (After Opening)": total_after,
            "New User Share (%)": round(new_ratio, 1),
            "Migrated User Share (%)": round(migrated_ratio, 1)
        })

    result_df = pd.DataFrame(results)
    with open('user_activity_data.txt', 'w') as file:
        print("📊 New and Migrated Users by Station Group:\n")
        print(result_df)
    return result_df

#ábra

def share_of_users_by_station_group_figure_generator(result_df):
    groups = result_df['Station Group']
    new_ratio = result_df['New User Share (%)']
    migrated_ratio = result_df['Migrated User Share (%)']

    x = np.arange(len(groups))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, new_ratio, width, label='New Users (%)', color='#1f77b4')
    bars2 = ax.bar(x + width/2, migrated_ratio, width, label='Migrated Users (%)', color='#ff7f0e')

    ax.set_title('Share of New and Migrated Users by Station Group', fontsize=14, weight='bold')
    ax.set_xlabel('Station Group', fontsize=12)
    ax.set_ylabel('Share (%)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=15, ha='right')
    ax.legend(title='User Type')

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()
    plt.savefig('Share of New and Migrated Users by Station Group')

# másik ábra: felhasználók száma az új állomásokon a bevezetést követő 90 napban
def figure_generator_about_user_number_in_90_days(result_df):
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(result_df))
    bars = ax.bar(x, result_df['Total (After Opening)'], color='#2ca02c')

    ax.set_title('Total Unique Users by Station Group (90 Days After Opening)',
                 fontsize=14, weight='bold')
    ax.set_xlabel('Station Group', fontsize=12)
    ax.set_ylabel('Number of Unique Users', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(result_df['Station Group'], rotation=15, ha='right')

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

    plt.savefig('Total Unique Users by Station Group (90 Days After Opening)')