import geopandas as gpd
from dotenv import load_dotenv
load_dotenv()
from app.site_search import SiteSearch

def main():
    # Load GIS data
    plots_gdf = gpd.read_file('data/GIS/2261_dzialki_egib_wfs_gml.gml')
    roads_gdf = gpd.read_file('data/GIS/2261_ulice_egib_wfs_gml.gml')
    buildings_gdf = gpd.read_file('data/GIS/2261_budynki_egib_wfs_gml.gml')
    churches_gdf = gpd.read_file('data/GIS/churches.gpkg')
    green_areas_gdf = gpd.read_file('data/GIS/green_areas.gpkg')
    noise_map_gdf = gpd.read_file('data/GIS/noise/noise_map.gpkg')
    senior_density_path = 'data/GIS/old_heatmap.tif'
    
    # Set CRS for all data
    plots_gdf.set_crs("EPSG:2177", inplace=True)
    
    # Initialize site search
    site_search = SiteSearch(
        plots_gdf=plots_gdf,
        roads_gdf=roads_gdf,
        buildings_gdf=buildings_gdf,
        churches_gdf=churches_gdf,
        green_areas_gdf=green_areas_gdf,
        noise_map_gdf=noise_map_gdf,
        senior_density_raster_path=senior_density_path
    )
    
    # Find candidates
    candidates = site_search.find_candidates()
    
    # Print results
    print(f"\nFound {len(candidates)} potential sites")
    print("\nTop 5 candidates:")
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"\n{i}. Plot {candidate.plot_id}")
        print(f"   Score: {candidate.score:.2f}")
        print(f"   Area: {candidate.area:.0f} sqm")
        print(f"   Shape index: {candidate.shape_index:.2f}")
        print(f"   Distance to nearest green area: {candidate.distance_to_nearest_green:.0f}m")
        print(f"   Distance to nearest church: {candidate.distance_to_nearest_church:.0f}m")
        print(f"   Noise level: {candidate.noise_level:.0f} dB")
        print(f"   Senior density: {candidate.senior_density:.1f}%")
    
    # Visualize results
    site_search.visualize_candidates(candidates)

if __name__ == "__main__":
    main() 