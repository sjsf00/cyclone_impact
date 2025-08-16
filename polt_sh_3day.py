import pandas as pd
import matplotlib.pyplot as plt
import glob

fileList = glob.glob('flight_data_3day_gd_df_*.csv')
df_list = []

for file in fileList:
    df = pd.read_csv(file)
    df_list.append(df)

flight_data_3day_gd_df = pd.concat(df_list).drop_duplicates()

flight_data_3day_gd_df['utc_time'] = pd.to_datetime(flight_data_3day_gd_df['timestamp'], utc=True)
flight_data_3day_gd_df['china_time'] = flight_data_3day_gd_df['utc_time'].dt.tz_convert('Asia/Shanghai')


flight_data_3day_gd_df['year'] = flight_data_3day_gd_df['china_time'].dt.year
flight_data_3day_gd_df['month'] = flight_data_3day_gd_df['china_time'].dt.month
flight_data_3day_gd_df['day'] = flight_data_3day_gd_df['china_time'].dt.day
flight_data_3day_gd_df['hour'] = flight_data_3day_gd_df['china_time'].dt.hour
flight_data_3day_gd_df['quarter_hour'] = (flight_data_3day_gd_df['china_time'].dt.minute // 15) + 1


hourly_counts = (
    flight_data_3day_gd_df
    .groupby(['day', 'hour'])['callsign']
    .nunique()
    .reset_index()
    .rename(columns={'callsign': 'unique_aircraft_count'})
)

# plot with different color per day
plt.figure(figsize=(10, 6))
for day, group in hourly_counts.groupby('day'):
    plt.plot(group['hour'], group['unique_aircraft_count'], marker='o', label=f'Day {day}')

plt.xlabel('Hour of Day (China Time)')
plt.ylabel('Unique Aircraft Count')
plt.title('Hourly Unique Aircraft Counts by Day')
plt.legend(title='Day')
plt.grid(True)
plt.tight_layout()
plt.show()