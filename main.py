from app.programming import get_inputs
from app.site_search import SiteSearch
import geopandas as gpd

def main():
    # Step 1: Get project requirements
    print("\n=== Step 1: Define Project Requirements ===")
    retirement_home = get_inputs()
    gfa_range = retirement_home.calculate_gfa_range()
    plot_range = retirement_home.calculate_plot_size_range()
    
    print("\n=== Project Requirements Summary ===")
    print(f"Residents: {retirement_home.min_residents} - {retirement_home.max_residents}")
    print(f"Required GFA: {gfa_range[0]:.0f} - {gfa_range[1]:.0f} sqm")
    print(f"Required Plot Size: {plot_range[0]:.0f} - {plot_range[1]:.0f} sqm")
    
    # Step 2: Load GIS data
    print("\n=== Step 2: Loading GIS Data ===")
    plots_gdf = gpd.read_file('data/GIS/2261_dzialki_egib_wfs_gml.gml')
    roads_gdf = gpd.read_file('data/GIS/2261_ulice_egib_wfs_gml.gml')
    buildings_gdf = gpd.read_file('data/GIS/2261_budynki_egib_wfs_gml.gml')
    churches_gdf = gpd.read_file('data/GIS/churches.gpkg')
    green_areas_gdf = gpd.read_file('data/GIS/green_areas.gpkg')
    noise_map_gdf = gpd.read_file('data/GIS/noise/noise_map.gpkg')
    senior_density_path = 'data/GIS/old_heatmap.tif'
    
    # Ensure all data is in EPSG:2177
    plots_gdf.set_crs("EPSG:2177", inplace=True)
    roads_gdf.set_crs("EPSG:2177", inplace=True)
    buildings_gdf.set_crs("EPSG:2177", inplace=True)
    churches_gdf = churches_gdf.to_crs("EPSG:2177")
    green_areas_gdf = green_areas_gdf.to_crs("EPSG:2177")
    noise_map_gdf = noise_map_gdf.to_crs("EPSG:2177")
    
    # Step 3: Initialize site search with project requirements
    print("\n=== Step 3: Searching for Sites ===")
    site_search = SiteSearch(
        plots_gdf=plots_gdf,
        roads_gdf=roads_gdf,
        buildings_gdf=buildings_gdf,
        churches_gdf=churches_gdf,
        green_areas_gdf=green_areas_gdf,
        noise_map_gdf=noise_map_gdf,
        senior_density_raster_path=senior_density_path
    )
    
    # Update constraints based on project requirements
    site_search.constraints.min_plot_area = plot_range[0]
    site_search.constraints.max_plot_area = plot_range[1]
    
    # Find and display candidates
    candidates = site_search.find_candidates()
    
    # Step 4: Display Results
    print(f"\n=== Step 4: Found {len(candidates)} Potential Sites ===")
    if candidates:
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
        
        # Step 5: Visualize Results
        print("\n=== Step 5: Generating Visualizations ===")
        site_search.visualize_candidates(candidates)
    else:
        print("\nNo suitable sites found with the given requirements.")
        print("Consider adjusting the project parameters and try again.")

if __name__ == "__main__":
    main() 