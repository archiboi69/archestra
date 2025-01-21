import geopandas as gpd
import pandas as pd
import numpy as np
import contextily as ctx
import matplotlib.pyplot as plt
from typing import List, Optional
from shapely.geometry import Polygon
from .models import SiteConstraints, SitePenaltyWeights, SiteCandidate, NormalizationRanges

class SiteSearch:
    def __init__(self, 
                 plots_gdf: gpd.GeoDataFrame,
                 roads_gdf: gpd.GeoDataFrame,
                 buildings_gdf: gpd.GeoDataFrame,
                 green_areas_gdf: gpd.GeoDataFrame,
                 noise_map_gdf: gpd.GeoDataFrame):
        """Initialize with all required geodataframes for site search"""
        self.plots = plots_gdf
        self.roads = roads_gdf
        self.buildings = buildings_gdf
        self.green_areas = green_areas_gdf
        self.noise_map = noise_map_gdf
        
        # Set default constraints and weights
        self.constraints = SiteConstraints()
        self.weights = SitePenaltyWeights()
    
    def find_candidates(self) -> List[SiteCandidate]:
        """Find and rank potential sites based on constraints and scoring"""
        candidates = []
        
        # Apply hard constraints
        potential_sites = self._apply_hard_constraints()
        if potential_sites.empty:
            print("No potential sites found after applying hard constraints")
            return []
        print(f"\nFound {len(potential_sites)} sites after applying hard constraints")
        
        # Create GeoDataFrame with centroids for efficient distance calculations
        potential_centroids = gpd.GeoDataFrame(
            geometry=potential_sites.geometry.centroid,
            crs=potential_sites.crs
        )
        
        # Calculate all distances efficiently using GeoSeries operations
        print("\nCalculating distances...")
        
        # Green areas distances
        green_distances = potential_centroids.geometry.apply(
            lambda x: self.green_areas.distance(x).min()
        )
        print(f"Green areas distance range: {green_distances.min():.1f} - {green_distances.max():.1f} meters")
        
        # Calculate noise levels using spatial join
        print("\nCalculating noise levels...")
        noise_data = gpd.sjoin(
            potential_sites[['geometry']],
            self.noise_map[['geometry', 'min_noise']],
            predicate='intersects'
        )
        noise_levels = noise_data.groupby(level=0)['min_noise'].mean().fillna(50)
        print(f"Noise level range: {noise_levels.min():.1f} - {noise_levels.max():.1f} dB")
        
        # Create normalization ranges
        self.norm_ranges = NormalizationRanges(
            min_green_distance=float(green_distances.min()),
            max_green_distance=float(green_distances.max()),
            min_noise=float(50),
            max_noise=float(noise_levels.max())
        )
        
        print("\nNormalization ranges:")
        for field, value in self.norm_ranges.__dict__.items():
            print(f"{field}: {value:.1f}")
        
        # Create candidates using the pre-calculated ranges
        print("\nCreating candidates...")
        for idx, plot in potential_sites.iterrows():
            candidate = self._create_candidate(plot)
            if candidate is not None:
                candidates.append(candidate)
        
        # Sort by score in descending order (higher is better)
        candidates.sort(key=lambda x: x.score)
        print(f"\nCreated {len(candidates)} valid candidates")
        
        return candidates
    
    def _apply_hard_constraints(self) -> gpd.GeoDataFrame:
        """Apply hard constraints to find potential sites"""
        # Filter by area using geometry.area directly
        sized_plots = self.plots[
            (self.plots.geometry.area >= self.constraints.min_plot_area) & 
            (self.plots.geometry.area <= self.constraints.max_plot_area)
        ]
        
        # Calculate shape index
        sized_plots['shape_index'] = sized_plots.geometry.apply(self._calculate_shape_index)
        shaped_plots = sized_plots[sized_plots['shape_index'] >= self.constraints.min_shape_index]
        
        # Filter out plots with residential buildings
        residential_buildings = self.buildings[self.buildings['FUNKCJA'] == 'budynki mieszkalne']
        plots_with_buildings = gpd.sjoin(
            shaped_plots, 
            residential_buildings, 
            how='inner',
            rsuffix='_bldg'
        )
        empty_plots = shaped_plots[~shaped_plots.index.isin(plots_with_buildings.index)].drop_duplicates(subset='gml_id')
        
        # Filter by road accessibility
        road_plots = gpd.sjoin(
            self.plots,
            self.roads,
            how='inner',
            predicate='intersects',
            rsuffix='_road'
        )
        
        potential_sites = gpd.sjoin(
            empty_plots,
            road_plots,
            how='inner',
            predicate='touches',
            rsuffix='_roadplot'
        ).drop_duplicates(subset='gml_id')
        
        if potential_sites.empty:
            print("No potential sites found after applying hard constraints")
            return gpd.GeoDataFrame(columns=empty_plots.columns, crs=empty_plots.crs)
        
        return potential_sites
    
    def _calculate_shape_index(self, geometry: Polygon) -> float:
        """Calculate shape regularity index (4πA/P²)"""
        area = geometry.area
        perimeter = geometry.length
        return 4 * np.pi * area / (perimeter ** 2)
    
    def _create_candidate(self, plot: gpd.GeoSeries) -> Optional[SiteCandidate]:
        """Create a SiteCandidate from a plot with all metrics calculated"""
        try:
            # Create base candidate
            candidate = SiteCandidate(
                plot_id=plot['gml_id'],
                geometry=plot.geometry,
                area=plot.geometry.area,
                shape_index=plot['shape_index'],
            )
            
            # Calculate metrics
            candidate.distance_to_nearest_green = self._calculate_distance_to_nearest(
                plot.geometry.centroid, self.green_areas
            )
            
            # Get noise level and handle NaN values
            noise_intersections = gpd.sjoin(
                gpd.GeoDataFrame(geometry=[plot.geometry], crs=self.noise_map.crs),
                self.noise_map[['geometry', 'min_noise']],
                predicate='intersects'
            )
            candidate.noise_level = noise_intersections['min_noise'].mean() if not noise_intersections.empty else 50
            
            # Calculate score using pre-calculated ranges
            candidate.calculate_score(self.weights, self.norm_ranges)
            
            return candidate
            
        except Exception as e:
            print(f"Error creating candidate for plot {plot['gml_id']}: {str(e)}")
            return None
    
    def _calculate_distance_to_nearest(self, point, target_gdf: gpd.GeoDataFrame) -> float:
        """Calculate distance to nearest feature in target geodataframe"""
        distances = [point.distance(geom) for geom in target_gdf.geometry]
        return round(min(distances))
    
    def visualize_candidates(self, candidates: List[SiteCandidate], n_top: int = 6):
        """Visualize top N candidates on a map"""
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Convert penalties to percentage scores (0 penalty = 100%, 1 penalty = 0%)
        display_scores = [(1 - c.score) * 100 for c in candidates]
        
        # Create GeoDataFrame from candidates
        candidate_gdf = gpd.GeoDataFrame(
            geometry=[c.geometry for c in candidates],
            data={
                'score': display_scores,
                'plot_id': [c.plot_id for c in candidates]
            },
            crs=self.plots.crs
        )
        
        # Plot all candidates with transparency
        for idx, (candidate, display_score) in enumerate(zip(candidates, display_scores)):
            color = 'red' if idx < n_top else 'gray'
            alpha = 0.8 if idx < n_top else 0.2
            gpd.GeoSeries([candidate.geometry]).plot(
                ax=ax,
                color=color,
                alpha=alpha
            )
            
            # Add labels for top candidates
            if idx < n_top:
                centroid = candidate.geometry.centroid
                ax.annotate(
                    f"#{idx+1}\nScore: {display_score:.0f}%\n"
                    f"Area: {candidate.area:.0f}m²",
                    xy=(centroid.x, centroid.y),
                    ha='center',
                    va='center',
                    fontsize=8
                )
        
        # Add basemap with explicit CRS
        ctx.add_basemap(
            ax,
            crs=self.plots.crs.to_string(),
            source=ctx.providers.CartoDB.Positron
        )
        
        ax.set_axis_off()
        plt.title(f"Top {n_top} Site Candidates")
        plt.show()
        
        # Create detail views
        if n_top > 0:
            self.visualize_candidate_details(candidates[:n_top])
    
    def visualize_candidate_details(self, candidates: List[SiteCandidate]):
        """Create detailed views of each candidate site"""
        buffer_distance = 300  # meters
        
        # Calculate grid dimensions
        n = len(candidates)
        cols = min(3, n)
        rows = (n + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
        if rows == 1 and cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        for idx, candidate in enumerate(candidates):
            ax = axes[idx]
            
            # Create buffer for context area
            buffer = candidate.geometry.buffer(buffer_distance)
            
            # Get features in view
            noise_in_view = self.noise_map[self.noise_map.intersects(buffer)]
            plots_in_view = self.plots[self.plots.intersects(buffer)]
            buildings_in_view = self.buildings[self.buildings.intersects(buffer)]
            green_in_view = self.green_areas[self.green_areas.intersects(buffer)]
            
            # Plot layers
            noise_in_view.plot(ax=ax, cmap='Reds', alpha=0.3)
            plots_in_view.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.3)
            buildings_in_view.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.3)
            green_in_view.plot(ax=ax, color='green', alpha=0.3)
            
            # Highlight the candidate site
            site_gdf = gpd.GeoDataFrame(geometry=[candidate.geometry], crs=self.plots.crs)
            site_gdf.plot(ax=ax, facecolor='red', edgecolor='black', alpha=0.7, linewidth=2)
            
            # Set bounds
            ax.set_xlim(buffer.bounds[0], buffer.bounds[2])
            ax.set_ylim(buffer.bounds[1], buffer.bounds[3])
            
            # Add title with metrics
            ax.set_title(
                f"Site {idx+1}\n"
                f"Area: {candidate.area:.0f}m²\n"
                f"Score: {(1 - candidate.score) * 100:.0f}%\n"
                f"Noise: {candidate.noise_level:.0f}dB"
            )
            ax.set_axis_off()
        
        # Remove empty subplots
        for idx in range(len(candidates), len(axes)):
            fig.delaxes(axes[idx])
        
        plt.tight_layout()
        plt.show() 