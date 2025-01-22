from app.programming import get_inputs
from app.site_search import SiteSearch
from app.development_conditions import DevelopmentConditions
import geopandas as gpd

def select_site(candidates):
    """Allow user to select a site for further analysis"""
    while True:
        try:
            print("\nEnter the number of the site you want to analyze (1-6), or 0 to exit:")
            choice = int(input("Your choice: "))
            if choice == 0:
                return None
            if 1 <= choice <= min(6, len(candidates)):
                return candidates[choice - 1]
            print("Invalid choice! Please select a number between 1 and 6.")
        except ValueError:
            print("Please enter a valid number!")

def main():
    # Step 1: Get project requirements
    print("\n=== Step 1: Define Project Requirements ===")
    program_data = get_inputs()
    
    # Calculate plot size range based on projected GFA
    # Assuming FAR (Floor Area Ratio) range of 0.8 to 2.0
    min_plot_size = program_data['projected_gfa'] / 2.0  # Maximum FAR scenario
    max_plot_size = program_data['projected_gfa'] / 0.8  # Minimum FAR scenario
    
    print("\n=== Project Requirements Summary ===")
    print(f"Current GFA: {program_data['current_gfa']:.0f} sqm")
    print(f"Projected GFA: {program_data['projected_gfa']:.0f} sqm")
    print(f"Required Plot Size: {min_plot_size:.0f} - {max_plot_size:.0f} sqm")
    
    # Step 2: Load GIS data
    print("\n=== Step 2: Loading GIS Data ===")
    plots_gdf = gpd.read_file('data/GIS/EGIB/2261_dzialki_egib_wfs_gml.gml')
    roads_gdf = gpd.read_file('data/GIS/EGIB/2261_ulice_egib_wfs_gml.gml')
    buildings_gdf = gpd.read_file('data/GIS/budynki_2022.gpkg')
    green_areas_gdf = gpd.read_file('data/GIS/green_areas.gpkg')
    noise_map_gdf = gpd.read_file('data/GIS/noise/noise_map.gpkg')
    
    # Load transportation data
    bus_tram_stops_gdf = gpd.read_file('data/GIS/przystanki_tram_bus.gpkg')
    train_stops_gdf = gpd.read_file('data/GIS/przystanki_kolej.gpkg')
    airport_gdf = gpd.read_file('data/GIS/airport.gpkg')
    
    # Ensure all data is in EPSG:2177
    plots_gdf.set_crs("EPSG:2177", inplace=True)
    roads_gdf.set_crs("EPSG:2177", inplace=True)
    buildings_gdf.set_crs("EPSG:2177", inplace=True)
    green_areas_gdf = green_areas_gdf.to_crs("EPSG:2177")
    noise_map_gdf = noise_map_gdf.to_crs("EPSG:2177")
    bus_tram_stops_gdf = bus_tram_stops_gdf.to_crs("EPSG:2177")
    train_stops_gdf = train_stops_gdf.to_crs("EPSG:2177")
    airport_gdf = airport_gdf.to_crs("EPSG:2177")
    
    # Step 3: Initialize site search with project requirements
    print("\n=== Step 3: Searching for Sites ===")
    site_search = SiteSearch(
        plots_gdf=plots_gdf,
        roads_gdf=roads_gdf,
        buildings_gdf=buildings_gdf,
        green_areas_gdf=green_areas_gdf,
        noise_map_gdf=noise_map_gdf,
        bus_tram_stops_gdf=bus_tram_stops_gdf,
        train_stops_gdf=train_stops_gdf,
        airport_gdf=airport_gdf
    )
    
    # Update constraints based on project requirements
    site_search.constraints.min_plot_area = min_plot_size
    site_search.constraints.max_plot_area = max_plot_size
    
    # Find and display candidates
    candidates = site_search.find_candidates()
    
    # Step 4: Display Results
    print(f"\n=== Step 4: Found {len(candidates)} Potential Sites ===")
    if candidates:
        print("\nTop 6 candidates:")
        for i, candidate in enumerate(candidates[:6], 1):
            print(f"\n{i}. Plot {candidate.plot_id}")
            print(f"   Score: {candidate.score:.2f}")
            print(f"   Area: {candidate.area:.0f} sqm")
            print(f"   Shape index: {candidate.shape_index:.2f}")
            print(f"   Distance to nearest green area: {candidate.distance_to_nearest_green:.0f}m")
            print(f"   Noise level: {candidate.noise_level:.0f} dB")
        
        # Step 5: Visualize Results
        print("\n=== Step 5: Generating Visualizations ===")
        site_search.visualize_candidates(candidates)
        
        # Step 6: Select Site for Development Analysis
        print("\n=== Step 6: Select Site for Development Analysis ===")
        selected_site = select_site(candidates)
        if selected_site:
            print(f"\nSelected Plot {selected_site.plot_id} for development analysis.")
            print("\nSite Details:")
            print(f"Area: {selected_site.area:.0f} sqm")
            print(f"Shape index: {selected_site.shape_index:.2f}")
            print(f"Score: {selected_site.score:.2f}")
            
            # Step 7: Analyze Development Conditions
            print("\n=== Step 7: Analyzing Development Conditions ===")
            development = DevelopmentConditions(
                site_candidate=selected_site,
                plots_gdf=plots_gdf,
                roads_gdf=roads_gdf,
                buildings_gdf=buildings_gdf
            )
            
            try:
                conditions = development.analyze()
                print("\nDevelopment Conditions:")
                print(f"Building Coverage Ratio: {conditions['coverage_ratio_min']:.2f} - {conditions['coverage_ratio_max']:.2f}")
                print(f"Floor Area Ratio: {conditions['floor_area_ratio']:.2f}")
                print(f"Maximum Height: {conditions['height']:.1f}m")
                print(f"Front Width: {conditions['front_width']:.1f}m")
                print(f"Setback: {conditions['setback']:.1f}m")
                print(f"Frontage Length: {conditions['frontage_length']:.1f}m")
                print(f"Analysis Radius: {conditions['analysis_radius']:.1f}m")
                
                # Add Requirements vs Development Conditions Summary
                print("\n=== Requirements vs Development Conditions Summary ===")
                print("\nGross Floor Area (GFA):")
                print(f"Current Required: {program_data['current_gfa']:.0f} m²")
                print(f"Future Required: {program_data['projected_gfa']:.0f} m²")
                print(f"Estimated Possible: {conditions['estimated_gfa']:.0f} m²")
                
                # Check if estimated GFA meets requirements
                if conditions['estimated_gfa'] < program_data['projected_gfa']:
                    print("WARNING: Estimated GFA is below projected requirement!")
                else:
                    print("✓ Estimated GFA meets projected requirements")
                
                print("\nPlot Size:")
                print(f"Required: {min_plot_size:.0f} - {max_plot_size:.0f} m²")
                print(f"Actual: {conditions['site_area']:.0f} m²")
                
                # Check if plot size meets requirements
                if conditions['site_area'] < min_plot_size:
                    print("WARNING: Plot is too small!")
                elif conditions['site_area'] > max_plot_size:
                    print("WARNING: Plot is larger than necessary!")
                else:
                    print("✓ Plot size meets requirements")
                
                # Visualize development conditions
                print("\nGenerating development conditions visualization...")
                development.visualize()
                
                # Export development conditions to DXF
                print("\nExporting development conditions to DXF...")
                output_file = f"output/site_{selected_site.plot_id}_conditions.dxf"
                development.export_to_dxf(output_file)
                print(f"DXF file saved to: {output_file}")
                
                return selected_site, conditions
                
            except ValueError as e:
                print(f"\nError analyzing development conditions: {str(e)}")
                print("Please select a different site.")
                return None, None
        else:
            print("\nNo site selected for development analysis.")
            return None, None
    else:
        print("\nNo suitable sites found with the given requirements.")
        print("Consider adjusting the project parameters and try again.")
        return None, None

if __name__ == "__main__":
    selected_site, conditions = main()
    
    if selected_site and conditions:
        print("\nSite selection and development conditions analysis complete.")