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
    
    def __init__(
        self, 
        version, 
        min_residents, 
        max_residents, 
        stories,
        quality_level=None,
        staffing_benchmarks=None
    ):
        self.version = version
        self.min_residents = min_residents
        self.max_residents = max_residents
        self.stories = stories
        self.quality_level = quality_level
        self.staffing_benchmarks = staffing_benchmarks
        
        # Store staffing metrics if available
        if staffing_benchmarks is not None:
            self.nurse_aide_hours = staffing_benchmarks['Reported Nurse Aide Staffing Hours per Resident per Day']
            self.lpn_hours = staffing_benchmarks['Reported LPN Staffing Hours per Resident per Day']
            self.rn_hours = staffing_benchmarks['Reported RN Staffing Hours per Resident per Day']
            self.pt_hours = staffing_benchmarks['Reported Physical Therapist Staffing Hours per Resident Per Day']
            
            # Calculate total staff hours per day
            self.total_staff_hours = (
                self.nurse_aide_hours + 
                self.lpn_hours + 
                self.rn_hours + 
                self.pt_hours
            )
        else:
            self.nurse_aide_hours = 0
            self.lpn_hours = 0
            self.rn_hours = 0
            self.pt_hours = 0
            self.total_staff_hours = 0

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

@dataclass
class SitePenaltyWeights:
    """Weights for different penalty factors in site scoring"""
    green_penalty: float = 0.4     # Weight for distance to green areas
    church_penalty: float = 0.2    # Weight for distance to churches
    noise_penalty: float = 0.3     # Weight for noise level
    senior_penalty: float = 0.1    # Weight for senior population density

@dataclass
class NormalizationRanges:
    """Pre-calculated min/max values for normalization"""
    min_green_distance: float
    max_green_distance: float
    min_church_distance: float
    max_church_distance: float
    min_noise: float
    max_noise: float
    min_senior: float
    max_senior: float

@dataclass
class SiteCandidate:
    """A potential site for the retirement home"""
    plot_id: str
    geometry: Polygon
    area: float                    # Plot area in sqm
    shape_index: float             # Shape regularity index (4πA/P²)
    
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
    
    def calculate_score(self, weights: SitePenaltyWeights, ranges: NormalizationRanges) -> float:
        """Calculate site suitability score based on penalty weights"""
        if any(x is None for x in [
            self.distance_to_nearest_green,
            self.distance_to_nearest_church,
            self.noise_level,
            self.senior_density
        ]):
            raise ValueError("All metrics must be set before calculating score")
        
        def normalize(value: float, min_val: float, max_val: float) -> float:
            """Normalize value to 0-1 range where 0 is best"""
            if max_val == min_val:
                return 0
            return (value - min_val) / (max_val - min_val)
        
        # Calculate penalties using pre-calculated ranges
        green_penalty = normalize(
            self.distance_to_nearest_green,
            ranges.min_green_distance,
            ranges.max_green_distance
        )
        
        church_penalty = normalize(
            self.distance_to_nearest_church,
            ranges.min_church_distance,
            ranges.max_church_distance
        )
        
        noise_penalty = normalize(
            np.log(self.noise_level),
            np.log(ranges.min_noise),
            np.log(ranges.max_noise)
        )
        
        senior_penalty = 1 - normalize(
            self.senior_density,
            ranges.min_senior,
            ranges.max_senior
        )  # Invert so higher density = lower penalty
        
        # Calculate weighted score
        self.score = (
            green_penalty * weights.green_penalty +
            church_penalty * weights.church_penalty +
            noise_penalty * weights.noise_penalty +
            senior_penalty * weights.senior_penalty
        )
        
        return self.score 