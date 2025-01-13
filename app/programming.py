from app.models import RetirementHome
import pandas as pd

DEFAULTS = {
    "coverage_ratio": 0.3,        # Building footprint / Plot area
    "quality_levels": {
        1: "Basic Care",          # Corresponds to CMS 1-2 star
        2: "Standard Care",       # Corresponds to CMS 3 star
        3: "Premium Care"         # Corresponds to CMS 4-5 star
    }
}

VALID_RANGES = {
    "sqm_per_resident": (50, 100),        # Total GFA per resident including all spaces
    "stories": (1, 5),
    "resident_count": (1, 300),           # Total number of residents
    "coverage_ratio": (0.15, 0.4),        # Min and max coverage ratios
    "quality_level": (1, 3)               # Quality levels from basic to premium
}

def load_staffing_benchmarks():
    """Load and process CMS nursing home data to get staffing benchmarks by quality level"""
    try:
        df = pd.read_csv('data/NHCompare/NH_ProviderInfo_Nov2024.csv')
        
        # Group homes by overall rating and calculate median staffing metrics
        staffing_benchmarks = df.groupby('Overall Rating').agg({
            'Reported Nurse Aide Staffing Hours per Resident per Day': 'median',
            'Reported LPN Staffing Hours per Resident per Day': 'median',
            'Reported RN Staffing Hours per Resident per Day': 'median',
            'Reported Physical Therapist Staffing Hours per Resident Per Day': 'median'
        }).fillna(0)
        
        # Map CMS ratings to our quality levels
        quality_staffing = {
            1: staffing_benchmarks.loc[1:2].mean(),  # Basic: avg of 1-2 star homes
            2: staffing_benchmarks.loc[3],           # Standard: 3 star homes
            3: staffing_benchmarks.loc[4:5].mean()   # Premium: avg of 4-5 star homes
        }
        
        return quality_staffing
    except Exception as e:
        print(f"Warning: Could not load staffing benchmarks: {e}")
        return None

def get_inputs():
    print("\n=== Retirement Home Programming Calculator ===")
    
    # Version tracking
    version = input("Version number: ")
    
    # Get quality level
    print("\nQuality Levels:")
    for level, description in DEFAULTS['quality_levels'].items():
        print(f"{level}: {description}")
    
    while True:
        try:
            quality_level = int(input(
                f"\nSelect quality level ({VALID_RANGES['quality_level'][0]}-{VALID_RANGES['quality_level'][1]}): "
            ))
            if VALID_RANGES['quality_level'][0] <= quality_level <= VALID_RANGES['quality_level'][1]:
                break
            print("Invalid quality level! Please select from available options.")
        except ValueError:
            print("Please enter a number!")

    # Get resident range
    while True:
        try:
            min_residents = int(input(
                f"\nMinimum number of residents ({VALID_RANGES['resident_count'][0]}-{VALID_RANGES['resident_count'][1]}): "
            ))
            max_residents = int(input(
                f"Maximum number of residents ({VALID_RANGES['resident_count'][0]}-{VALID_RANGES['resident_count'][1]}): "
            ))
            
            if (VALID_RANGES['resident_count'][0] <= min_residents <= VALID_RANGES['resident_count'][1] and
                VALID_RANGES['resident_count'][0] <= max_residents <= VALID_RANGES['resident_count'][1] and
                min_residents <= max_residents):
                break
            print("Invalid range! Make sure min ≤ max and both are within valid limits.")
        except ValueError:
            print("Please enter numbers!")
    
    # Get sqm per resident
    while True:
        try:
            sqm_per_resident = int(input(f"Total GFA per resident ({VALID_RANGES['sqm_per_resident'][0]}-{VALID_RANGES['sqm_per_resident'][1]}): "))
            if VALID_RANGES['sqm_per_resident'][0] <= sqm_per_resident <= VALID_RANGES['sqm_per_resident'][1]:
                break
            print("Invalid number of stories! Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a number!")
    
    # Get stories
    while True:
        try:
            stories = int(input(f"Number of stories ({VALID_RANGES['stories'][0]}-{VALID_RANGES['stories'][1]}): "))
            if VALID_RANGES['stories'][0] <= stories <= VALID_RANGES['stories'][1]:
                break
            print("Invalid number of stories! Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a number!")
    
    # Load staffing benchmarks based on quality level
    staffing_benchmarks = load_staffing_benchmarks()
    
    retirement_home = RetirementHome(
        version=version,
        min_residents=min_residents,
        max_residents=max_residents,
        stories=stories,
        quality_level=quality_level,
        staffing_benchmarks=staffing_benchmarks[quality_level] if staffing_benchmarks else None
    )
    return retirement_home