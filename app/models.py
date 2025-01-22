from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from shapely.geometry import Polygon
import numpy as np

@dataclass
class SiteConstraints:
    """Hard constraints for site selection"""
    min_plot_area: float = 3500    # Minimum plot area in sqm
    max_plot_area: float = 7500    # Maximum plot area in sqm
    min_shape_index: float = 0.6   # Minimum shape regularity index

@dataclass
class SitePenaltyWeights:
    """Weights for different penalty factors in site scoring"""
    green_penalty: float = 0.3     # Weight for distance to green areas
    noise_penalty: float = 0.3     # Weight for noise level
    transport_penalty: float = 0.4  # Weight for transportation accessibility
    
    # Transportation sub-weights (should sum to 1.0)
    bus_tram_weight: float = 0.5   # Most important for daily commute
    train_weight: float = 0.3      # Important for regional access
    airport_weight: float = 0.2    # Less important but valuable for business

@dataclass
class NormalizationRanges:
    """Pre-calculated min/max values for normalization"""
    min_green_distance: float
    max_green_distance: float
    min_noise: float
    max_noise: float
    min_bus_tram_distance: float
    max_bus_tram_distance: float
    min_train_distance: float
    max_train_distance: float
    min_airport_distance: float
    max_airport_distance: float

@dataclass
class SiteCandidate:
    """A potential site for the office building"""
    plot_id: str
    geometry: Polygon
    area: float                    # Plot area in sqm
    shape_index: float             # Shape regularity index (4πA/P²)
    
    # Scoring metrics
    distance_to_nearest_green: Optional[float] = None  # Distance to nearest green area
    noise_level: Optional[float] = None  # Noise level in dB
    distance_to_bus_tram: Optional[float] = None
    distance_to_train: Optional[float] = None
    distance_to_airport: Optional[float] = None
    
    score: float = 0.0            # Final site suitability score
    
    def meets_constraints(self, constraints: SiteConstraints) -> bool:
        """Check if site meets all hard constraints"""
        return (
            constraints.min_plot_area <= self.area <= constraints.max_plot_area and
            self.shape_index >= constraints.min_shape_index
        )
    
    def calculate_score(self, weights: SitePenaltyWeights, ranges: NormalizationRanges) -> float:
        """Calculate site suitability score based on penalty weights"""
        if any(x is None for x in [
            self.distance_to_nearest_green,
            self.noise_level,
            self.distance_to_bus_tram,
            self.distance_to_train,
            self.distance_to_airport
        ]):
            raise ValueError("All metrics must be set before calculating score")
        
        def normalize(value: float, min_val: float, max_val: float) -> float:
            """Normalize value to 0-1 range where 0 is best"""
            if max_val == min_val:
                return 0
            return (value - min_val) / (max_val - min_val)
        
        # Calculate individual penalties
        green_penalty = normalize(
            self.distance_to_nearest_green,
            ranges.min_green_distance,
            ranges.max_green_distance
        )
        
        noise_penalty = normalize(
            np.log(self.noise_level),
            np.log(ranges.min_noise),
            np.log(ranges.max_noise)
        )
        
        # Calculate transportation penalties
        bus_tram_penalty = normalize(
            self.distance_to_bus_tram,
            ranges.min_bus_tram_distance,
            ranges.max_bus_tram_distance
        )
        
        train_penalty = normalize(
            self.distance_to_train,
            ranges.min_train_distance,
            ranges.max_train_distance
        )
        
        airport_penalty = normalize(
            self.distance_to_airport,
            ranges.min_airport_distance,
            ranges.max_airport_distance
        )
        
        # Calculate composite transport penalty
        transport_penalty = (
            bus_tram_penalty * weights.bus_tram_weight +
            train_penalty * weights.train_weight +
            airport_penalty * weights.airport_weight
        )
        
        # Calculate final score
        self.score = (
            green_penalty * weights.green_penalty +
            noise_penalty * weights.noise_penalty +
            transport_penalty * weights.transport_penalty
        )
        
        return self.score 