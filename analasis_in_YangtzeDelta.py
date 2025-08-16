import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.read_file('China_Province.geojson')
flights = pd.read_csv('historic_flight_positions_YangtzeDelta.csv')
typhoon_track_hourly = pd.read_stata('typhoon_track_hourly_202507.dta')
gdf_district = gpd.read_file('China_District.geojson')

flights = flights.dropna(subset=['lat', 'lon', 'timestamp']).copy()#nothing happened here

gdf_flights = gpd.GeoDataFrame(
    flights,
    geometry=gpd.points_from_xy(flights['lon'], flights['lat']),
    crs="EPSG:4326"   # FR24 lat/lon are in WGS84
)



target_province = ['安徽省', '江苏省', '浙江省', '上海市']
gdf_target = gdf[gdf['name'].isin(target_province)]


gdf_flights = gpd.GeoDataFrame(
    flights,
    geometry=gpd.points_from_xy(
        flights.lon,
        flights.lat
    ),
    crs="EPSG:4326"
)

# 只保留在目标省份范围内的点（空间过滤）
gdf_flights = gpd.sjoin(gdf_flights, gdf_target, predicate="within")

# 解析时间戳
gdf_flights['timestamp'] = pd.to_datetime(gdf_flights['timestamp'], errors='coerce')

# 筛选时间范围


# 按天分组绘图
fig, axes = plt.subplots(2, 4, figsize=(14, 24))
axes = axes.flatten()

dates = pd.date_range('2025-07-28', '2025-08-03')
for i, date in enumerate(dates):
    ax = axes[i]
    gdf_target.boundary.plot(ax=ax, color="black", linewidth=1)

    day_data = gdf_flights[gdf_flights['timestamp'].dt.date == date.date()]
    day_data.plot(ax=ax, color="red", markersize=5, alpha=0.6)

    count_points = len(day_data)
    ax.set_title(f"{date.date()} — Total Points: {count_points}", fontsize=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

plt.tight_layout()
plt.show()
