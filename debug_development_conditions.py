import geopandas as gpd
from app.development_conditions import DevelopmentConditions

def main():
    # Load required GIS data
    print("Loading GIS data...")
    plots = gpd.read_file("data/GIS/2261_dzialki_egib_wfs_gml.gml")
    roads = gpd.read_file("data/GIS/2261_ulice_egib_wfs_gml.gml")
    buildings = gpd.read_file("data/GIS/budynki_2022.gpkg")

    plots.set_crs(epsg=2177, inplace=True)
    roads.set_crs(epsg=2177, inplace=True)
    buildings.set_crs(epsg=2177, inplace=True)
    
    # Get the specific site
    site_gml_id = 'dzialki.238458'
    site = plots[plots['gml_id'] == site_gml_id].iloc[0]
    print(f"Found site: {site_gml_id}")
    
    try:
        # Create development conditions object
        print("\nAnalyzing development conditions...")
        dev_conditions = DevelopmentConditions(site, plots, roads, buildings)
        
        # Run analysis
        conditions = dev_conditions.analyze()
        
        # Print results
        print("\nDevelopment Conditions Results:")
        print(f"Coverage Ratio (min-max): {conditions['coverage_ratio_min']:.2f}-{conditions['coverage_ratio_max']:.2f}")
        print(f"Floor Area Ratio: {conditions['floor_area_ratio']:.2f}")
        print(f"Height: {conditions['height']:.1f}m")
        print(f"Front Width: {conditions['front_width']:.1f}m")
        print(f"Setback: {conditions['setback']:.1f}m")
        print(f"Frontage Length: {conditions['frontage_length']:.1f}m")
        print(f"Site Area: {conditions['site_area']:.1f}m²")
        print(f"Estimated GFA: {conditions['estimated_gfa']:.1f}m²")
        
        # Visualize
        print("\nGenerating visualization...")
        dev_conditions.visualize()
        
        # Export to DXF
        print("\nExporting to DXF...")
        output_file = f"output/site_{site_gml_id}_conditions.dxf"
        dev_conditions.export_to_dxf(output_file)
        print(f"DXF file saved to: {output_file}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise

if __name__ == "__main__":
    main() 