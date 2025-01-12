from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from shapely.geometry import Polygon
import numpy as np

@dataclass
class RetirementHome:
    """Core programming requirements for a retirement home"""
    version: str                   # For tracking iterations
    min_residents: int            # Minimum number of residents
    max_residents: int            # Maximum number of residents
    stories: int = 3              # Default number of stories
    coverage_ratio: float = 0.3   # Building footprint / Plot area
    sqm_per_resident: float = 70  # Total GFA per resident including all spaces
    
    def calculate_gfa_range(self) -> Tuple[float, float]:
        """Calculate min and max Gross Floor Area"""
        min_gfa = self.min_residents * self.sqm_per_resident
        max_gfa = self.max_residents * self.sqm_per_resident
        return (min_gfa, max_gfa)
    
    def calculate_plot_size_range(self) -> Tuple[float, float]:
        """Calculate the required plot size range based on GFA and coverage ratio"""
        gfa_min, gfa_max = self.calculate_gfa_range()
        
        # Calculate footprint area ranges using coverage ratio
        min_plot_size = gfa_min / (self.stories * self.coverage_ratio)
        max_plot_size = gfa_max / (self.stories * self.coverage_ratio)
        
        return min_plot_size, max_plot_size

@dataclass
class SiteConstraints:
    """Hard constraints for site selection"""
    min_plot_area: float = 3500    # Minimum plot area in sqm
    max_plot_area: float = 7500    # Maximum plot area in sqm
    min_shape_index: float = 0.6   # Minimum shape regularity index
    max_distance_to_road: float = 10  # Maximum distance to road in meters

@dataclass
class SitePenaltyWeights:
    """Weights for different penalty factors in site scoring"""
    green_penalty: float = 0.4     # Weight for distance to green areas
    church_penalty: float = 0.2    # Weight for distance to churches
    noise_penalty: float = 0.3     # Weight for noise level
    senior_penalty: float = 0.1    # Weight for senior population density

@dataclass
class SiteCandidate:
    """A potential site for the retirement home"""
    plot_id: str
    geometry: Polygon
    area: float                    # Plot area in sqm
    shape_index: float             # Shape regularity index (4πA/P²)
    distance_to_road: float        # Distance to nearest road in meters
    
    # Scoring metrics
    distance_to_nearest_green: Optional[float] = None  # Distance to nearest green area
    distance_to_nearest_church: Optional[float] = None  # Distance to nearest church
    noise_level: Optional[float] = None  # Noise level in dB
    senior_density: Optional[float] = None  # Senior population density
    
    score: float = 0.0            # Final site suitability score
    
    def meets_constraints(self, constraints: SiteConstraints) -> bool:
        """Check if site meets all hard constraints"""
        return (
            constraints.min_plot_area <= self.area <= constraints.max_plot_area and
            self.shape_index >= constraints.min_shape_index and
            self.distance_to_road <= constraints.max_distance_to_road
        )
    
    def calculate_score(self, weights: SitePenaltyWeights) -> float:
        """Calculate site suitability score based on penalty weights"""
        if any(x is None for x in [
            self.distance_to_nearest_green,
            self.distance_to_nearest_church,
            self.noise_level,
            self.senior_density
        ]):
            raise ValueError("All metrics must be set before calculating score")
        
        # Normalize metrics to 0-1 range where 0 is best (least penalty)
        green_penalty = self.distance_to_nearest_green / 1000  # Assuming max 1km
        church_penalty = self.distance_to_nearest_church / 1000  # Assuming max 1km
        noise_penalty = (self.noise_level - 50) / 20  # Assuming 50-70dB range
        senior_penalty = 1 - (self.senior_density / 100)  # Assuming 0-100% range
        
        # Clip penalties to 0-1 range
        green_penalty = np.clip(green_penalty, 0, 1)
        church_penalty = np.clip(church_penalty, 0, 1)
        noise_penalty = np.clip(noise_penalty, 0, 1)
        senior_penalty = np.clip(senior_penalty, 0, 1)
        
        # Calculate weighted score
        self.score = (
            green_penalty * weights.green_penalty +
            church_penalty * weights.church_penalty +
            noise_penalty * weights.noise_penalty +
            senior_penalty * weights.senior_penalty
        )
        
        return self.score 