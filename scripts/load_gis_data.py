import geopandas as gpd
from sqlalchemy import create_engine
import sys
from pathlib import Path
from shapely.geometry import MultiPolygon, Polygon, LineString, MultiLineString
import pandas as pd
import json
import numpy as np

def standardize_geometry(gdf, geom_type='polygon'):
    """Standardize geometry types and CRS"""
    # First ensure CRS is set to EPSG:2177
    if gdf.crs is None or gdf.crs != 'EPSG:2177':
        print(f"Converting CRS from {gdf.crs} to EPSG:2177")
        gdf = gdf.set_crs('EPSG:2177', allow_override=True)
    
    if geom_type == 'polygon':
        # Convert geometries to MultiPolygon where needed
        def to_multi(geom):
            if geom is None:
                return None
            if isinstance(geom, Polygon):
                return MultiPolygon([geom])
            elif isinstance(geom, MultiPolygon):
                return geom
            else:
                print(f"Warning: Unexpected geometry type: {type(geom)}")
                return None
        
        gdf.geometry = gdf.geometry.apply(to_multi)
    
    elif geom_type == 'linestring':
        # Convert geometries to MultiLineString where needed
        def to_multi_line(geom):
            if geom is None:
                return None
            if isinstance(geom, LineString):
                return MultiLineString([geom])
            elif isinstance(geom, MultiLineString):
                return geom
            else:
                print(f"Warning: Unexpected geometry type: {type(geom)}")
                return None
        
        gdf.geometry = gdf.geometry.apply(to_multi_line)
    
    return gdf

def calculate_shape_index(geometry):
        area = geometry.area
        perimeter = geometry.length
        return 4 * np.pi * area / (perimeter * perimeter)

def load_data_with_relationships(data_dir):
    """Load and process all datasets"""
    # Load datasets
    plots_gdf = gpd.read_file(data_dir / "GIS/EGIB/2261_dzialki_egib_wfs_gml.gml")
    roads_gdf = gpd.read_file(data_dir / "GIS/EGIB/2261_ulice_egib_wfs_gml.gml")
    buildings_gdf = gpd.read_file(data_dir / "GIS/PL.PZGiK.336.BDOT10k.2261__OT_BUBD_A.gpkg")
    
    # Standardize geometries and CRS
    plots_gdf = standardize_geometry(plots_gdf, 'polygon')
    buildings_gdf = standardize_geometry(buildings_gdf, 'polygon')
    roads_gdf = standardize_geometry(roads_gdf, 'linestring')
    
    # Process sites
    sites_gdf = process_sites(plots_gdf, roads_gdf)
    
    # Process buildings
    buildings_gdf = process_buildings(buildings_gdf, sites_gdf)
    
    return sites_gdf, buildings_gdf

def process_sites(plots_gdf, roads_gdf):
    """Process and filter sites"""
    
    # Filter out plots that are too small or too large
    plots_gdf['area'] = plots_gdf.geometry.area
    plots_gdf = plots_gdf[
        (plots_gdf['area'] >= 500) & 
        (plots_gdf['area'] <= 20000)
    ]
    print(f"After size filtering: {len(plots_gdf)} plots remaining")
    
    # Filter out plots with poor shape index
    plots_gdf['shape_index'] = plots_gdf.geometry.apply(calculate_shape_index)
    plots_gdf = plots_gdf[plots_gdf['shape_index'] > 0.6]
    print(f"After shape index filtering: {len(plots_gdf)} plots remaining")

    # Remove road plots
    road_plots = gpd.sjoin(plots_gdf, roads_gdf, predicate='intersects', lsuffix='plots', rsuffix='roads')
    plots_gdf = plots_gdf[~plots_gdf.index.isin(road_plots.index.unique())]
    print(f"After removing road plots: {len(plots_gdf)} plots remaining")
    
    # Find road access
    road_access = get_road_access(plots_gdf, road_plots)
    
    # Create sites dataframe
    sites_gdf = plots_gdf.copy()
    sites_gdf = sites_gdf.rename(columns={
        'ID_DZIALKI': 'id_egib',
        'NAZWA_OBREBU': 'district'
    })
    
    # Add road access info
    sites_gdf = sites_gdf.merge(
        road_access[['site_id_egib', 'road_id_egib', 'road_name', 'frontage_length']], 
        left_on='id_egib', 
        right_on='site_id_egib',
        how='left'
    )
    
    sites_gdf = sites_gdf.rename(columns={
        'road_id_egib': 'access_road_id',
        'road_name': 'access_road_name'
    })
    
    return sites_gdf

def process_buildings(buildings_gdf, sites_gdf):
    """Process buildings and establish site relationships"""
    # Calculate building metrics
    buildings_gdf['area'] = buildings_gdf.geometry.area
    buildings_gdf['height'] = calculate_building_height(buildings_gdf)
    
    # Clean up columns
    buildings_gdf = buildings_gdf.rename(columns={
        'IDEGIB': 'id_egib',
        'LICZBAKONDYGNACJI': 'stories',
        'KODKST': 'kst_class',
        'FUNKCJAOGOLNABUDYNKU': 'function'
    })
    
    # Find which site each building belongs to
    building_sites = gpd.sjoin(buildings_gdf, sites_gdf, how='inner', predicate='within')
    buildings_gdf['site_id_egib'] = building_sites['id_egib_right']

    # Calculate front width
    buildings_gdf['front_width'] = calculate_front_width(buildings_gdf)
    return buildings_gdf

def calculate_building_height(buildings_gdf):
    """Calculate building height based on stories"""
    return buildings_gdf['stories'] * 3.0  # Assuming 3m per story

def calculate_front_width(buildings_gdf):
    """Calculate building front width"""
    return buildings_gdf.geometry.apply(lambda g: g.minimum_rotated_rectangle.length)

def get_road_side(plot_geom, road_geom, buffer_distance=0.1):
    """Get the road-facing side of a plot."""
    # Create a small buffer around the road polygon
    road_buffer = road_geom.buffer(buffer_distance)
    
    # Get the plot boundary
    plot_boundary = plot_geom.boundary
    
    # Find the intersection with the road buffer
    road_side = plot_boundary.intersection(road_buffer)
    
    # Handle different geometry types
    if road_side.is_empty:
        return None
        
    if hasattr(road_side, 'geoms'):  # MultiLineString or GeometryCollection
        # Get all LineString parts
        line_parts = [geom for geom in road_side.geoms 
                     if geom.geom_type == 'LineString' and geom.length >= 0.01]
        if not line_parts:
            return None
        # Return the longest part
        return max(line_parts, key=lambda x: x.length)
    
    elif road_side.geom_type == 'LineString':
        if road_side.length < 0.01:  # Using 1cm as minimum length
            return None
        return road_side
    
    else:
        print(f"Warning: Unexpected geometry type: {road_side.geom_type}")
        return None

def get_road_access(sites_gdf, road_plots):
    """Find road access using road plots"""
    
    # Find sites that touch road plots
    print("Finding sites with direct road access...")
    sites_with_access = gpd.sjoin(sites_gdf, road_plots, predicate='touches')
    
    results = []
    # For each unique site
    for site_idx in sites_with_access.index.unique():
        site_geom = sites_gdf.loc[site_idx].geometry
        
        # Get road indices, handling both single value and Series cases
        road_indices = sites_with_access.loc[site_idx, 'index_right']
        if isinstance(road_indices, pd.Series):
            touching_road_indices = road_indices.unique()
        else:
            touching_road_indices = [road_indices]  # Single value case
            
        # Find the road with longest boundary
        longest_boundary = 0
        best_road = None
        
        for road_idx in touching_road_indices:
            try:
                road = road_plots.loc[road_idx]
                road_side = get_road_side(site_geom, road.geometry)
                if road_side is not None:
                    boundary_length = road_side.length
                    if boundary_length > longest_boundary:
                        longest_boundary = boundary_length
                        best_road = road
            except KeyError:
                print(f"Warning: Road index {road_idx} not found in road_plots")
                continue
        
        if best_road is not None:
            results.append({
                'site_id_egib': sites_gdf.loc[site_idx, 'ID_DZIALKI'],
                'road_id_egib': best_road['ID_DZIALKI'],
                'road_name': best_road['nazwa_ulicy'],
                'frontage_length': longest_boundary
            })
    
    return pd.DataFrame(results)

def load_to_database(engine, sites_gdf, buildings_gdf):
    """Load processed data into database"""
    print("Loading sites...")
    sites_gdf.to_postgis('sites', engine, if_exists='append', index=True)
    
    print("Loading buildings...")
    buildings_gdf.to_postgis(
        'buildings',
        engine,
        if_exists='append',
        index=True,
        index_label='id'
    )

def main():
    # Assuming the script is in scripts/ directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    sites_gdf, buildings_gdf = load_data_with_relationships(data_dir)
    print(sites_gdf.head())
    print(buildings_gdf.head())

if __name__ == "__main__":
    sys.exit(main()) 