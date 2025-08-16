import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import matplotlib
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import List, Union
import time
from shapely.geometry import box, Point, MultiPolygon, Polygon
from shapely.ops import unary_union



matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


gdf = gpd.read_file("China_Province.geojson")


def keep_largest_polygon(geometry):

    if isinstance(geometry, MultiPolygon):
        largest_polygon = max(geometry.geoms, key=lambda p: p.area)
        return largest_polygon
    elif isinstance(geometry, Polygon):
        return geometry
    else:
        return geometry
    
gdf['main_geometry'] = gdf['geometry'].apply(keep_largest_polygon)

def create_intersecting_grid(
    source_gdf: gpd.GeoDataFrame,
    province_name_column: str,
    target_provinces: List[str], 
    grid_size: float,
    geom_column: str = 'main_geometry',
    plot_result: bool = True,
    plot_filename: str = 'preview_grid.png'
) -> Union[gpd.GeoDataFrame, None]:

    try:
        print(f"target_provinces: {target_provinces}")
        target_gdf = source_gdf[source_gdf[province_name_column].isin(target_provinces)].copy()
        
        if target_gdf.empty:
            raise ValueError(f"No provinces found in the target list: {target_provinces}")
        
        target_gdf = target_gdf.set_geometry(geom_column)
        
        combined_geom = target_gdf.geometry.unary_union
        
        minx, miny, maxx, maxy = combined_geom.bounds
        x_coords = np.arange(minx, maxx, grid_size)
        y_coords = np.arange(miny, maxy, grid_size)
        grid_cells = [box(x, y, x + grid_size, y + grid_size) for x in x_coords for y in y_coords]
        print(f"Total {len(grid_cells)} grid cells created.")
        
        intersecting_cells = [cell for cell in grid_cells if cell.intersects(combined_geom)]
        print(f"Left {len(intersecting_cells)} grid cells after filtering.")
        
        grid_gdf = gpd.GeoDataFrame(geometry=intersecting_cells, crs=source_gdf.crs)
        
        if plot_result:
            print("\nploting...")
            fig, ax = plt.subplots(1, 1, figsize=(12, 12))
            target_gdf.plot(ax=ax, edgecolor='black', facecolor='lightblue', linewidth=1)
            grid_gdf.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=0.8)
            ax.set_title(f"Provinces with {grid_size}x{grid_size} Degree Intersecting Grid")
            fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
            
        return grid_gdf
    except Exception as e:
        print(f"Error in create_intersecting_grid: {e}")
        return None
    
def convert_grid_gdf_to_query_format(
    grid_gdf: gpd.GeoDataFrame,
    geom_column: str = 'geometry'
) -> List[dict]:

    query_format = []
    for _, row in grid_gdf.iterrows():
        geom = row[geom_column]
        west, south, east, north = geom.bounds
        query_format.append({
            'north': north,
            'south': south,
            'west': west,
            'east': east,
        })
    return query_format
   
if __name__ == "__main__":
    target_provinces = ['上海市', '江苏省', '浙江省','安徽省']
    grid_size = 2.0  # 2.0 degree grid size
    
    grid_gdf = create_intersecting_grid(gdf, 'name', target_provinces, grid_size)
    
    if grid_gdf is not None:
        print("Grid creation successful.")
        grid_gdf.to_file("intersecting_grid_for_YangtzeDelta.shp")
    else:
        print("Grid creation failed.")
        
    query_format = convert_grid_gdf_to_query_format(grid_gdf)
    with open("query_format_YangtzeDelta.json", "w") as f:
        json.dump(query_format, f, indent=4)