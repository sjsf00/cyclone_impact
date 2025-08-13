import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data
flight_data_3day_df = pd.read_csv("flight_data_3day_df.csv")

# Convert to datetime with timezone
flight_data_3day_df['utc_time'] = pd.to_datetime(flight_data_3day_df['timestamp'], utc=True)
flight_data_3day_df['china_time'] = flight_data_3day_df['utc_time'].dt.tz_convert('Asia/Shanghai')


flight_data_3day_df['year'] = flight_data_3day_df['china_time'].dt.year
flight_data_3day_df['month'] = flight_data_3day_df['china_time'].dt.month
flight_data_3day_df['day'] = flight_data_3day_df['china_time'].dt.day
flight_data_3day_df['hour'] = flight_data_3day_df['china_time'].dt.hour
flight_data_3day_df['quarter_hour'] = (flight_data_3day_df['china_time'].dt.minute // 15) + 1


# Round down to nearest 15 minutes to group by quarter hour
flight_data_3day_df['quarter_start'] = flight_data_3day_df['china_time'].dt.floor('15T')

# Remove duplicate callsigns in the same quarter
quarter_counts = (
    flight_data_3day_df
    .drop_duplicates(subset=['callsign', 'quarter_start'])
    .groupby('quarter_start')
    .size()
    .reset_index(name='unique_aircraft_count')
)

# Plot with actual China time on x-axis
plt.figure(figsize=(12, 6))
plt.plot(quarter_counts['quarter_start'], quarter_counts['unique_aircraft_count'], marker='o')
plt.xlabel('China Time')
plt.ylabel('Unique Aircraft Count')
plt.title('Unique Aircraft Count per Quarter-Hour (China Time)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


hourly_counts = (
    flight_data_3day_df
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

event_day = 30
baseline_day = 29

event_counts = hourly_counts.query("day == @event_day")[['hour', 'unique_aircraft_count']]
baseline_counts = hourly_counts.query("day == @baseline_day")[['hour', 'unique_aircraft_count']]

# Rename columns for clarity
event_counts = event_counts.rename(columns={'unique_aircraft_count': 'event_count'})
baseline_counts = baseline_counts.rename(columns={'unique_aircraft_count': 'baseline_count'})

# Merge by hour
merged = pd.merge(event_counts, baseline_counts, on='hour', how='inner')

# Calculate relative change
merged['pct_change'] = (merged['event_count'] - merged['baseline_count']) / merged['baseline_count'] * 100
merged['abs_change'] = merged['event_count'] - merged['baseline_count']
print(merged)


fig, ax1 = plt.subplots(figsize=(12,6))

# 画左y轴
ax1.plot(merged['hour'], merged['pct_change'], color='tab:blue', marker='o', label='Pct Change (%)')
ax1.set_xlabel('Hour')
ax1.set_ylabel('Pct Change (%)', color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')
ax1.grid(True)

# 右边y轴画abs_change
ax2 = ax1.twinx()
ax2.plot(merged['hour'], merged['abs_change'], color='tab:red', marker='s', label='Abs Change')
ax2.set_ylabel('Abs Change', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')

# 添加图例（合并两个轴的图例）
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

plt.title('Pct Change and Abs Change over Hours')
plt.show()