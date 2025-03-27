import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point, LineString
from typing import Optional, List, Dict, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons import text2path
from ezdxf.addons.text2path import Kind  # Import Kind enum

def get_road_neighbors(site_polygon, plots_gdf: gpd.GeoDataFrame, roads_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Get neighboring plots that have significant road access (intersection > 1m)."""
    # Get all neighbors
    neighbors = plots_gdf[plots_gdf.geometry.touches(site_polygon)]
    
    # Join with roads
    road_neighbors = gpd.sjoin(neighbors, roads_gdf, how='inner', predicate='intersects', lsuffix='neighbor', rsuffix='road')
    
    # Filter by intersection length
    min_road_length = 5.0  # minimum 5 meters of road frontage
    valid_neighbors = []
    
    for _, neighbor in road_neighbors.iterrows():
        intersection = neighbor.geometry.intersection(roads_gdf[roads_gdf['gml_id'] == neighbor['gml_id_road']].geometry.iloc[0])
        if intersection.length >= min_road_length:
            valid_neighbors.append(neighbor)
    
    if not valid_neighbors:
        return gpd.GeoDataFrame(columns=road_neighbors.columns, crs=road_neighbors.crs)
    
    # Create GeoDataFrame from valid neighbors
    valid_road_neighbors = gpd.GeoDataFrame(valid_neighbors, crs=road_neighbors.crs)
    
    # Drop duplicates and apply size filter
    unique_road_neighbors = valid_road_neighbors.drop_duplicates(subset='gml_id_neighbor')
    max_plot_area = 10000
    unique_road_neighbors = unique_road_neighbors[unique_road_neighbors.area <= max_plot_area]
    
    return unique_road_neighbors

def get_road_side(plot_geom, road_geom, buffer_distance=0.1) -> Optional[LineString]:
    """Get the road-facing side of a plot."""
    # Create a small buffer around the road polygon
    road_buffer = road_geom.buffer(buffer_distance)
    
    # Get the plot boundary
    plot_boundary = plot_geom.boundary
    
    # Find the intersection with the road buffer
    road_side = plot_boundary.intersection(road_buffer)
    
    # If we got a MultiLineString, convert it to the longest LineString
    if road_side.geom_type == 'MultiLineString':
        # Get the longest part
        road_side = max(road_side.geoms, key=lambda x: x.length)
    
    # Verify we have a valid road side with non-zero length
    if road_side.is_empty or road_side.length < 0.01:  # Using 1cm as minimum length
        print(f"Warning: Invalid road side found (length={road_side.length:.2f}m)")
        return None
        
    return road_side

def get_access_road(site_geom, road_neighbors: gpd.GeoDataFrame) -> Optional[gpd.GeoSeries]:
    """Get the access road of the plot defined as the road plot with the longest common boundary."""
    longest_boundary = 0
    site_access_road = None
    
    for _, road in road_neighbors.iterrows():
        road_side = get_road_side(site_geom, road.geometry)
        if road_side is not None:  # Only process valid road sides
            boundary_length = road_side.length
            if boundary_length > longest_boundary:
                longest_boundary = boundary_length
                site_access_road = road
    
    return site_access_road

def get_frontage_length(plot_polygon, site_access_road) -> float:
    """Get the frontage length of the site from the access road."""
    site_access_road_side = get_road_side(plot_polygon, site_access_road.geometry)
    return site_access_road_side.length if site_access_road_side else 0.0

def extend_line(line: LineString, distance: float = 20) -> LineString:
    """Extend a LineString in both directions."""
    # Get coordinates of the line
    coords = list(line.coords)
    
    # Get the first and last points
    p1 = Point(coords[0])
    p2 = Point(coords[-1])
    
    # Get the vector of the line
    vector = [(p2.x - p1.x), (p2.y - p1.y)]
    
    # Normalize the vector
    length = (vector[0]**2 + vector[1]**2)**0.5
    if length == 0:
        return line
    unit_vector = [v/length for v in vector]
    
    # Create new start and end points
    new_start = (
        p1.x - unit_vector[0] * distance,
        p1.y - unit_vector[1] * distance
    )
    new_end = (
        p2.x + unit_vector[0] * distance,
        p2.y + unit_vector[1] * distance
    )
    
    return LineString([new_start, coords[0], coords[-1], new_end])

def get_building_front_elevation(building_geom, road_side: LineString) -> LineString:
    """Get the width of building front by projecting onto road side line."""
    print(f"  Road side length: {road_side.length:.1f}m")
    
    # Handle MultiLineString by getting all coordinates
    if road_side.geom_type == 'MultiLineString':
        # Get all coordinates from all lines
        all_coords = []
        for line in road_side.geoms:
            all_coords.extend(list(line.coords))
        # Create a simplified line using first and last points
        simplified_road_side = LineString([all_coords[0], all_coords[-1]])
        print("  Converted MultiLineString to LineString")
    else:
        # If it's already a LineString, just use its endpoints
        coords = list(road_side.coords)
        simplified_road_side = LineString([coords[0], coords[-1]])
    
    # Extend the road side line to ensure proper projections
    extended_road_side = extend_line(simplified_road_side, distance=100)
    print(f"  Extended road side length: {extended_road_side.length:.1f}m")
    
    # Get all vertices of the building polygon
    vertices = list(building_geom.exterior.coords)
    print(f"  Building vertices: {len(vertices)}")
    
    # Project each vertex onto the extended road side and get their distances
    projections = []
    for vertex in vertices:
        point = Point(vertex)
        # Project point onto extended line
        proj_dist = extended_road_side.project(point)
        proj_point = extended_road_side.interpolate(proj_dist)
        
        # Calculate distance from point to projection
        dist_to_line = point.distance(proj_point)
        
        # Only keep projections within reasonable distance (e.g., 50m)
        if dist_to_line <= 50:
            projections.append(proj_dist)
    
    print(f"  Valid projections: {len(projections)}")
    
    if not projections:  # If no valid projections found
        print("  No valid projections found")
        return LineString()  # Return empty line
        
    # Get the min and max projections to find the extent
    min_proj = min(projections)
    max_proj = max(projections)
    
    # Get the points on the extended road side
    point_start = extended_road_side.interpolate(min_proj)
    point_end = extended_road_side.interpolate(max_proj)
    
    # Create the front elevation line
    result = LineString([point_start, point_end])
    print(f"  Resulting front elevation length: {result.length:.1f}m")
    return result

def translate_points(points: List[Tuple[float, float]], dx: float, dy: float) -> List[Tuple[float, float]]:
    """Translate a list of points by dx and dy."""
    return [(x + dx, y + dy) for x, y in points]

def get_translation_offset(geometry) -> Tuple[float, float]:
    """Calculate translation offset to move geometry near origin."""
    bounds = geometry.bounds  # Returns (minx, miny, maxx, maxy)
    return -bounds[0], -bounds[1]

class DevelopmentConditions:
    def __init__(self, site_candidate, plots_gdf: gpd.GeoDataFrame, roads_gdf: gpd.GeoDataFrame, buildings_gdf: gpd.GeoDataFrame):
        """Initialize with the selected site and required GIS data."""
        self.site = site_candidate
        self.plots = plots_gdf
        self.roads = roads_gdf
        self.buildings = buildings_gdf
        self.analysis_radius = None
        self.road_neighbors = None
        self.access_road = None
        self.road_side = None
        self.frontage_length = None
        self.plot_metrics = None
        
    def analyze(self) -> Dict:
        """Analyze development conditions for the site."""
        # Get road access information
        self.road_neighbors = get_road_neighbors(self.site.geometry, self.plots, self.roads)
        if self.road_neighbors.empty:
            raise ValueError("Site has no valid road access")
            
        self.access_road = get_access_road(self.site.geometry, self.road_neighbors)
        if self.access_road is None:
            raise ValueError("Could not determine site access road")
            
        self.road_side = get_road_side(self.site.geometry, self.access_road.geometry)
        if self.road_side is None:
            raise ValueError("Could not determine road-facing side of the site")
            
        self.frontage_length = get_frontage_length(self.site.geometry, self.access_road)
        self.analysis_radius = max(50, min(3 * self.frontage_length, 200))
        
        # Analyze built-up plots in the area
        self.plot_metrics = self._analyze_neighborhood()
        
        # Calculate zoning conditions
        conditions = self._calculate_zoning_conditions()
        
        return conditions
    
    def _analyze_neighborhood(self) -> pd.DataFrame:
        """Analyze built-up plots in the analysis area."""
        # Create analysis area
        analysis_area = gpd.GeoSeries([self.site.geometry]).buffer(self.analysis_radius)
        
        # Find plots in the analysis area
        analyzed_plots = self.plots[self.plots.geometry.intersects(analysis_area.iloc[0])]
        
        # Prepare building centroids for spatial join
        self.buildings['centroid'] = self.buildings.centroid
        building_centroids = self.buildings.set_geometry('centroid', inplace=False).set_crs(self.buildings.crs)
        
        # Find built-up plots
        built_up_plots = gpd.sjoin(analyzed_plots, building_centroids, how='inner', 
                                  predicate='intersects', lsuffix='plot', rsuffix='building')
        
        plot_metrics = []
        
        for _, plot in built_up_plots.iterrows():
            plot_area = plot.geometry.area
            
            # Get buildings on this plot
            plot_buildings = self.buildings[self.buildings['GID'].isin(
                built_up_plots[built_up_plots['gml_id'] == plot['gml_id']]['GID']
            )]
            
            # Skip if no buildings found
            if plot_buildings.empty:
                continue
            
            # Calculate metrics
            bcr = plot_buildings.geometry.area.sum() / plot_area
            
            # Floor area ratio
            building_footprint = plot_buildings.geometry.area
            floors = plot_buildings['LICZBA_KONDYGNACJI']
            gross_floor_area = building_footprint * floors
            far = gross_floor_area.sum() / plot_area
            
            # Front width
            plot_road_neighbors = get_road_neighbors(plot.geometry, self.plots, self.roads)
            if plot_road_neighbors.empty:
                continue
                
            plot_access_road = get_access_road(plot.geometry, plot_road_neighbors)
            if plot_access_road is None:
                continue
                
            plot_road_side = get_road_side(plot.geometry, plot_access_road.geometry)
            if plot_road_side is None:
                continue
            
            # Process buildings for front elevation
            plot_front_elevations = []
            print(f"\nProcessing buildings for plot {plot['gml_id']}:")
            for _, building in plot_buildings.iterrows():
                building_processed = gpd.GeoSeries(building.geometry).union_all()
                front_elevation = get_building_front_elevation(building_processed, plot_road_side)
                print(f"  Building elevation length: {front_elevation.length:.1f}m")
                plot_front_elevations.append(front_elevation)
            
            # Get the longest front elevation
            if plot_front_elevations:
                longest_elevation = max(plot_front_elevations, key=lambda x: x.length)
                front_elevation_width = longest_elevation.length
                print(f"  Selected longest elevation: {front_elevation_width:.1f}m")
            else:
                front_elevation_width = 0
                print("  No valid front elevations found")
            
            # Check if plot is adjacent to the site and on the same access road
            adjacent = (plot.geometry.touches(self.site.geometry) and 
                       plot.geometry.touches(self.access_road.geometry))
            
            if adjacent:
                building_height = plot_buildings['WYSOKOSC'].max()
                setback = plot_buildings.geometry.distance(plot_road_side).min()
            else:
                building_height = None
                setback = None
            
            plot_metrics.append({
                'plot_id': plot['gml_id'],
                'building_coverage_ratio': bcr,
                'floor_area_ratio': far,
                'front_elevation_width': front_elevation_width,
                'adjacent': adjacent,
                'building_height': building_height,
                'setback': setback
            })
        
        return pd.DataFrame(plot_metrics).drop_duplicates(subset='plot_id')
    
    def _calculate_zoning_conditions(self) -> Dict:
        """Calculate zoning conditions based on neighborhood analysis."""
        # Coverage ratio from min to mean+20%
        coverage_ratio_min = float(self.plot_metrics['building_coverage_ratio'].min())
        coverage_ratio_max = float(self.plot_metrics['building_coverage_ratio'].mean() * 1.2)
        
        # Other metrics
        floor_area_ratio = float(self.plot_metrics['floor_area_ratio'].mean() * 1.2)
        height = self.plot_metrics['building_height'].mean()
        front_width = float(self.plot_metrics['front_elevation_width'].mean() * 1.2)
        
        # Handle missing setback values
        setback_values = self.plot_metrics['setback'].dropna()
        setback = float(setback_values.max()) if not setback_values.empty else 4.0  # default 4m setback
        
        # Calculate estimated GFA
        site_area = self.site.geometry.area
        estimated_gfa = site_area * floor_area_ratio
        
        return {
            'coverage_ratio_min': coverage_ratio_min,
            'coverage_ratio_max': coverage_ratio_max,
            'floor_area_ratio': floor_area_ratio,
            'height': height,
            'front_width': front_width,
            'setback': setback,
            'frontage_length': self.frontage_length,
            'analysis_radius': self.analysis_radius,
            'site_area': site_area,
            'estimated_gfa': estimated_gfa
        }
    
    def visualize(self, show_metrics: bool = True):
        """Visualize development conditions analysis."""
        if self.plot_metrics is None:
            raise ValueError("Must run analyze() before visualization")
            
        # Create analysis area
        analysis_area = gpd.GeoSeries([self.site.geometry]).buffer(self.analysis_radius)
        
        # Get built-up plots
        analyzed_plots = self.plots[self.plots.geometry.intersects(analysis_area.iloc[0])]
        self.buildings['centroid'] = self.buildings.centroid
        building_centroids = self.buildings.set_geometry('centroid', inplace=False).set_crs(self.buildings.crs)
        built_up_plots = gpd.sjoin(analyzed_plots, building_centroids, how='inner', 
                                  predicate='intersects', lsuffix='plot', rsuffix='building')
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot base layers
        built_up_plots.plot(ax=ax, color='orange', edgecolor='orange', alpha=0.5)
        if self.road_side:
            gpd.GeoSeries([self.road_side]).plot(ax=ax, color='red', linewidth=2)
        self.buildings.clip(built_up_plots.geometry.union_all()).plot(ax=ax, color='black', alpha=0.7)
        gpd.GeoSeries([self.site.geometry]).plot(ax=ax, color='red', alpha=0.5)
        
        if show_metrics:
            # Annotate plots with metrics
            for _, metrics in self.plot_metrics.iterrows():
                plot = built_up_plots[built_up_plots['gml_id'] == metrics['plot_id']]
                plot_geom = plot.geometry
                if not plot_geom.empty:
                    centroid = plot_geom.iloc[0].centroid
                    if metrics['adjacent']:
                        ax.annotate(
                            f"BSC: {metrics['building_coverage_ratio']:.2f}\n"
                            f"FAR: {metrics['floor_area_ratio']:.2f}\n"
                            f"H: {metrics['building_height']:.1f}m\n"
                            f"W: {metrics['front_elevation_width']:.1f}m", 
                            xy=(centroid.x, centroid.y),
                            xytext=(0, 0), 
                            textcoords='offset points',
                            ha='center', 
                            va='center', 
                            color='black',
                            fontsize=6
                        )
                    else:
                        ax.annotate(
                            f"BSC: {metrics['building_coverage_ratio']:.2f}\n"
                            f"FAR: {metrics['floor_area_ratio']:.2f}\n"
                            f"W: {metrics['front_elevation_width']:.1f}m",
                            xy=(centroid.x, centroid.y),
                            xytext=(0, 0), 
                            textcoords='offset points',
                            ha='center', 
                            va='center', 
                            color='white',
                            fontsize=6
                        )
            
            # Show setback area
            conditions = self._calculate_zoning_conditions()
            if pd.notna(conditions['setback']) and conditions['setback'] > 0:
                setback_area = self.site.geometry.intersection(
                    gpd.GeoSeries([self.road_side]).buffer(conditions['setback']).iloc[0]
                )
                if not setback_area.is_empty:
                    gpd.GeoSeries([setback_area]).plot(ax=ax, color='red', alpha=0.5)
                    # Add setback annotation
                    ax.annotate(
                        f"{conditions['setback']:.1f}m", 
                        xy=(setback_area.centroid.x, setback_area.centroid.y), 
                        ha='center', va='center', color='pink', fontsize=8
                    )
            
            # Add site metrics
            conditions = self._calculate_zoning_conditions()
            site_centroid = self.site.geometry.centroid
            ax.annotate(
                f"Requested:\n"
                f"BSC: {conditions['coverage_ratio_max']:.2f}\n"
                f"FAR: {conditions['floor_area_ratio']:.2f}\n"
                f"H: {conditions['height']:.1f}m\n"
                f"W: {conditions['front_width']:.1f}m\n"
                f"GFA: {conditions['estimated_gfa']:.0f}m²", 
                xy=(site_centroid.x, site_centroid.y), 
                ha='center', va='center', color='black', fontsize=10
            )
        
        ctx.add_basemap(ax, crs=self.plots.crs)
        ax.set_axis_off()
        plt.show() 
    
    def export_to_dxf(self, filename: str):
        """Export site and development conditions to DXF format."""
        if not hasattr(self, 'plot_metrics'):
            raise ValueError("Must run analyze() before exporting to DXF")
        
        # Create new DXF document
        doc = ezdxf.new("R2000")
        msp = doc.modelspace()
        
        # Calculate translation offset
        dx, dy = get_translation_offset(self.site.geometry)
        
        # Create layers
        doc.layers.add(name="SITE")
        site_layer = doc.layers.get("SITE")
        site_layer.color = 1  # Red
        
        doc.layers.add(name="SETBACK")
        setback_layer = doc.layers.get("SETBACK")
        setback_layer.color = 5  # Blue
        
        doc.layers.add(name="OFFSET")  # New layer for offset
        offset_layer = doc.layers.get("OFFSET")
        offset_layer.color = 3  # Green
        
        doc.layers.add(name="METRICS")
        metrics_layer = doc.layers.get("METRICS")
        metrics_layer.color = 7  # White/Black
        
        # Draw site boundary
        site_points = list(self.site.geometry.exterior.coords)
        translated_site = translate_points(site_points, dx, dy)
        site_polyline = msp.add_lwpolyline(translated_site)
        site_polyline.dxf.layer = "SITE"
        
        # Add 4m inward offset
        offset_geom = self.site.geometry.buffer(-4.0)
        if not offset_geom.is_empty:
            if offset_geom.geom_type == 'MultiPolygon':
                # If we got multiple polygons, use the largest one
                offset_geom = max(offset_geom.geoms, key=lambda x: x.area)
            offset_points = list(offset_geom.exterior.coords)
            translated_offset = translate_points(offset_points, dx, dy)
            offset_polyline = msp.add_lwpolyline(translated_offset)
            offset_polyline.dxf.layer = "OFFSET"
        
        # Draw setback area if available
        conditions = self._calculate_zoning_conditions()
        if self.road_side and pd.notna(conditions['setback']):
            setback_area = self.site.geometry.intersection(
                gpd.GeoSeries([self.road_side]).buffer(conditions['setback']).iloc[0]
            )
            if not setback_area.is_empty:
                setback_points = list(setback_area.exterior.coords)
                translated_setback = translate_points(setback_points, dx, dy)
                setback_polyline = msp.add_lwpolyline(translated_setback)
                setback_polyline.dxf.layer = "SETBACK"
        
        # Add metrics text
        site_centroid = self.site.geometry.centroid
        text_x, text_y = translate_points([(site_centroid.x, site_centroid.y)], dx, dy)[0]
        
        metrics = [
            f"Development Metrics:",
            f"BSC (Building Site Coverage): {conditions['coverage_ratio_max']:.2f}",
            f"FAR (Floor Area Ratio): {conditions['floor_area_ratio']:.2f}",
            f"W (Maximum Width): {conditions['front_width']:.1f}m",
            f"H (Maximum Height): {conditions['height']:.1f}m",
            f"Setback: {conditions['setback']:.1f}m",
            f"Site Area: {conditions['site_area']:.1f}m²",
            f"Estimated GFA: {conditions['estimated_gfa']:.1f}m²"
        ]
        
        # Add each line as paths
        line_height = 2.5  # Height between lines
        
        for i, line in enumerate(metrics):
            # Create text entity first
            text = msp.add_text(line)
            text.dxf.layer = "METRICS"
            text.dxf.height = 2.0  # Text height
            text.set_placement(
                (0, -i * line_height),  # insertion point
                align=TextEntityAlignment.TOP_RIGHT  # alignment
            )
            
            # Convert text entity to paths using LWPOLYLINES
            paths = text2path.virtual_entities(text, kind=Kind.LWPOLYLINES)
            
            # Add paths to modelspace and remove original text
            for entity in paths:
                entity.dxf.layer = "METRICS"
                msp.add_entity(entity)
            msp.delete_entity(text)
        
        # Save the DXF file
        doc.saveas(filename) 


def main():

    plots_gdf = gpd.read_file('data/GIS/2261_dzialki_egib_wfs_gml.gml')
    roads_gdf = gpd.read_file('data/GIS/2261_ulice_egib_wfs_gml.gml')
    buildings_gdf = gpd.read_file('data/GIS/budynki_2022.gpkg')
    site 
    
    development_conditions = DevelopmentConditions(site, plots, roads, buildings)
    development_conditions.analyze()
    development_conditions.visualize()
    #development_conditions.export_to_dxf("development_conditions.dxf")

if __name__ == "__main__":
    main()