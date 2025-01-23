import geopandas as gpd
from sqlalchemy import create_engine
from pathlib import Path
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import numpy as np
from typing import Tuple, Optional

def load_gis_datasets(data_dir: Path) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load GIS datasets from files.
    
    Args:
        data_dir: Path to data directory containing GIS files
        
    Returns:
        Tuple[GeoDataFrame, GeoDataFrame]: Plots and buildings geodataframes
    """
    plots_gdf = gpd.read_file(data_dir / "poznan/budynki_poznan.gml")
    buildings_gdf = gpd.read_file(data_dir / "poznan/PL.PZGiK.308.3064__OT_BUBD_A.xml")
    
    return plots_gdf, buildings_gdf

def standardize_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Standardize geometry to MultiPolygon and ensure correct CRS.
    
    Args:
        gdf: Input GeoDataFrame
        
    Returns:
        GeoDataFrame: DataFrame with standardized geometries
    """
    # Ensure CRS is set to EPSG:2177 (Poland CS92)
    if gdf.crs is None or gdf.crs != 'EPSG:2177':
        print(f"Converting CRS from {gdf.crs} to EPSG:2177")
        gdf = gdf.set_crs('EPSG:2177', allow_override=True)
    
    def to_multi(geom: Optional[Polygon]) -> Optional[MultiPolygon]:
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
    return gdf

def process_plots(plots_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Process and filter plots based on area and shape criteria.
    
    Args:
        plots_gdf: Raw plots GeoDataFrame
        
    Returns:
        GeoDataFrame: Filtered and processed plots
    """
    # Calculate metrics
    plots_gdf['area'] = plots_gdf.geometry.area
    plots_gdf['shape_index'] = plots_gdf.geometry.apply(
        lambda geom: 4 * np.pi * geom.area / (geom.length * geom.length)
    )
    
    # Apply filters
    valid_plots = plots_gdf[
        (plots_gdf['area'] >= 500) & 
        (plots_gdf['area'] <= 20000) &
        (plots_gdf['OZNACZENIE_UZYTKU'] != 'dr')
    ].copy()


    
    # Clean up columns
    valid_plots = valid_plots.rename(columns={
        'ID_DZIALKI': 'id_egib',
        'NAZWA_OBREBU': 'district'
    })
    
    print(f"Processed {len(valid_plots)} valid plots")
    return valid_plots

def check_road_access():

    road_plots = plots_gdf[plots_gdf['OZNACZENIE_UZYTKU'] == 'dr']



def process_buildings(buildings_gdf: gpd.GeoDataFrame, 
                     plots_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Process buildings and establish relationships with plots.
    
    Args:
        buildings_gdf: Raw buildings GeoDataFrame
        plots_gdf: Processed plots GeoDataFrame
        
    Returns:
        GeoDataFrame: Processed buildings with plot relationships
    """
    # Calculate metrics
    buildings_gdf['area'] = buildings_gdf.geometry.area
    buildings_gdf['height'] = buildings_gdf['LICZBAKONDYGNACJI'] * 3.0  # 3m per story
    
    # Clean up columns
    buildings_gdf = buildings_gdf.rename(columns={
        'IDEGIB': 'id_egib',
        'LICZBAKONDYGNACJI': 'stories',
        'KODKST': 'kst_class',
        'FUNKCJAOGOLNABUDYNKU': 'function'
    })
    
    # Establish plot relationships
    building_plots = gpd.sjoin(
        buildings_gdf, 
        plots_gdf, 
        how='inner', 
        predicate='within'
    )
    
    buildings_gdf['plot_id_egib'] = building_plots['id_egib_right']
    print(f"Processed {len(buildings_gdf)} buildings")
    
    return buildings_gdf

def save_to_database(engine: 'sqlalchemy.engine.Engine',
                    plots_gdf: gpd.GeoDataFrame,
                    buildings_gdf: gpd.GeoDataFrame) -> None:
    """
    Save processed data to PostGIS database.
    
    Args:
        engine: SQLAlchemy database engine
        plots_gdf: Processed plots GeoDataFrame
        buildings_gdf: Processed buildings GeoDataFrame
    """
    print("Saving to database...")
    
    plots_gdf.to_postgis(
        'plots',
        engine,
        if_exists='replace',
        index=True
    )
    
    buildings_gdf.to_postgis(
        'buildings',
        engine,
        if_exists='replace',
        index=True,
        index_label='id'
    )
    
    print("Database save completed")

def get_database_engine(config: dict) -> 'sqlalchemy.engine.Engine':
    """
    Create database engine from configuration.
    
    Args:
        config: Dictionary containing database configuration
        
    Returns:
        Engine: SQLAlchemy database engine
    """
    connection_string = (
        f"postgresql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )
    return create_engine(connection_string)

def main():
    """Main ETL process."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    try:
        # Load raw data
        print("Loading raw data...")
        plots_gdf, buildings_gdf = load_gis_datasets(data_dir)
        
        # Standardize geometries
        print("Standardizing geometries...")
        plots_gdf = standardize_geometry(plots_gdf)
        buildings_gdf = standardize_geometry(buildings_gdf)
        
        # Process datasets
        print("Processing plots...")
        plots_gdf = process_plots(plots_gdf)
        
        print("Processing buildings...")
        buildings_gdf = process_buildings(buildings_gdf, plots_gdf)
        
        # Optionally save to database
        # Uncomment and configure as needed
        # db_config = {
        #     'user': 'your_user',
        #     'password': 'your_password',
        #     'host': 'localhost',
        #     'port': 5432,
        #     'database': 'your_database'
        # }
        # engine = get_database_engine(db_config)
        # save_to_database(engine, plots_gdf, buildings_gdf)
        
    except Exception as e:
        print(f"Error during ETL process: {str(e)}")
        raise
    
    print("ETL process completed successfully")

if __name__ == "__main__":
    main()
