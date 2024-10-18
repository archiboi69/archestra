import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.strtree import STRtree

min_plot_area = 500 #sqm
max_plot_area = 10000 #sqm
min_shape_index = 0.6
max_distance_to_road = 10 #m

def calculate_shape_index(geometry):
    area = geometry.area
    perimeter = geometry.length
    return 4 * np.pi * area / (perimeter ** 2)

plots = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_dzialki_egib_wfs_gml.gml")
buildings = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_budynki_egib_wfs_gml.gml")
roads = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_ulice_egib_wfs_gml.gml")
local_plans = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/ZbiorAPP_MPZP_Gdansk.gml", layer="AktPlanowaniaPrzestrzennego")

plots.set_crs("EPSG:2177", inplace=True)
plots["area"] = plots.area
sized_plots = plots[(plots["area"] > min_plot_area) & (plots["area"] < max_plot_area)]

sized_plots['shape_index'] = sized_plots['geometry'].apply(calculate_shape_index)
shaped_plots = sized_plots[sized_plots['shape_index'] > min_shape_index]

# Dissolve local plans
area_with_local_plan = local_plans.dissolve(by="przestrzenNazw")

# Keep only shaped_plots that do not intersect with area_with_local_plan
shaped_plots_without_plan = gpd.overlay(shaped_plots, area_with_local_plan, how='difference')

# Filter residential buildings
residential_buildings = buildings[buildings['RODZAJ'] == 'm']

# Create spatial index for residential buildings
residential_tree = STRtree(residential_buildings.geometry.values)

# Function to check if a plot intersects with any residential building
def is_empty(geom):
    possible_matches_idx = residential_tree.query(geom)
    return not any(geom.intersects(residential_buildings.iloc[idx].geometry) for idx in possible_matches_idx)

# Apply the is_empty function to filter plots
empty_plots_without_plan = shaped_plots_without_plan[shaped_plots_without_plan.geometry.apply(is_empty)]

# Buffer the roads by 10 meters
buffered_roads = roads.buffer(max_distance_to_road)

# Find plots that intersect with the buffered roads
accessible_empty_plots = empty_plots_without_plan[empty_plots_without_plan.intersects(buffered_roads.union_all())]

print("Suitable plots found:", len(accessible_empty_plots))

# Plot the results
fig, ax = plt.subplots(figsize=(12, 8))
area_with_local_plan.plot(ax=ax, color='red', alpha=0.3)
plots.plot(ax=ax, color='grey', edgecolor='black')
accessible_empty_plots.plot(ax=ax, color='green')
buildings.plot(ax=ax, color='darkgrey', edgecolor='black')
residential_buildings.plot(ax=ax, color='black')
roads.plot(ax=ax, color='blue', linewidth=0.5)

plt.title('Suitable Plots')
plt.show()
