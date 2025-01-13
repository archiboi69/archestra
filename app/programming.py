from app.models import RetirementHome
import pandas as pd
import os

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

# Add new constants for space programming
SPACE_REQUIREMENTS = {
    "bedroom_areas": {
        "single": 16,  # m²
        "double": 22   # m²
    },
    "bathroom_areas": {
        "private": 4.5,  # m²
        "shared": 6    # m²
    },
    "bedroom_mix": {  # Single room percentage
        1: 0.20,  # Basic: 20% single rooms
        2: 0.50,  # Standard: 50% single rooms
        3: 1.00   # Premium: 100% single rooms
    },
    "bathroom_private_ratio": {
        1: 0.30,  # Basic: 30% private
        2: 0.70,  # Standard: 70% private
        3: 1.00   # Premium: 100% private
    },
    "per_resident_areas": {
        # (min area, area per resident) by quality level
        "extrovert": {
            1: (40, 2.5),
            2: (40, 3.0),
            3: (40, 4.0)
        },
        "semi_private": {
            1: (30, 2.0),
            2: (30, 2.5),
            3: (30, 3.0)
        },
        "introvert": {
            1: (20, 1.5),
            2: (20, 2.0),
            3: (20, 2.5)
        },
        "exercise": {
            1: (30, 1.0),
            2: (30, 1.5),
            3: (30, 2.0)
        },
        "workshop": {
            1: (25, 0.8),
            2: (25, 1.2),
            3: (25, 1.5)
        }
    }
}

# Add color coding for space types
SPACE_COLORS = {
    "Single Bedroom": "#E1C699",
    "Double Bedroom": "#E1C699",
    "Private Bathroom": "#A5D8DD",
    "Shared Bathroom": "#A5D8DD",
    "Extrovert Space": "#FFB6C1",
    "Semi-private Space": "#DDA0DD",
    "Introvert Space": "#E6E6FA",
    "Examination Room": "#98FB98",
    "Staff Office": "#F0E68C",
    "Staff Break Room": "#F0E68C",
    "Staff Lockers": "#F0E68C",
    "Exercise Space": "#FFA07A",
    "Workshop Space": "#87CEEB",
    "Circulation Seating": "#D3D3D3",
    "Public Bathroom": "#A5D8DD",
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

def calculate_space_requirements(home: RetirementHome) -> pd.DataFrame:
    """Calculate detailed space requirements based on retirement home parameters"""
    
    # Use maximum residents for space calculations
    resident_count = home.max_residents
    quality_level = home.quality_level
    
    # Calculate bedroom mix
    single_ratio = SPACE_REQUIREMENTS["bedroom_mix"][quality_level]
    single_rooms = int(resident_count * single_ratio)
    double_rooms = int((resident_count - single_rooms) / 2 + 0.5)  # Round up
    
    # Calculate bathroom counts
    private_ratio = SPACE_REQUIREMENTS["bathroom_private_ratio"][quality_level]
    total_rooms = single_rooms + double_rooms
    private_baths = int(total_rooms * private_ratio)
    shared_baths = total_rooms - private_baths
    
    # Calculate staff spaces
    peak_staff = int(home.total_staff_hours / 8 * 0.4)  # Assume 40% of daily staff at peak
    
    # Create space program table
    spaces = []
    
    # Residential
    spaces.extend([
        ("Single Bedroom", single_rooms, SPACE_REQUIREMENTS["bedroom_areas"]["single"]),
        ("Double Bedroom", double_rooms, SPACE_REQUIREMENTS["bedroom_areas"]["double"]),
        ("Private Bathroom", private_baths, SPACE_REQUIREMENTS["bathroom_areas"]["private"]),
        ("Shared Bathroom", shared_baths, SPACE_REQUIREMENTS["bathroom_areas"]["shared"])
    ])
    
    # Social and activity spaces
    for space_type in ["extrovert", "semi_private", "introvert", "exercise", "Workshop"]:
        min_area, area_per_resident = SPACE_REQUIREMENTS["per_resident_areas"][space_type][quality_level]
        total_area = max(min_area, resident_count * area_per_resident)
        spaces.append((
            f"{space_type.replace('_', ' ').title()} Space",
            1,
            total_area
        ))
    
    # Medical and staff spaces
    spaces.extend([
        ("Examination Room", max(1, resident_count // 40), 16),
        ("Staff Office", 1, 12 + 8 * (resident_count // 20)),
        ("Staff Break Room", 1, 20 + peak_staff),
        ("Staff Lockers", 1, 1.5 * peak_staff)
    ])
    
    # Support spaces
    corridor_seats = max(2, resident_count // 10)
    public_bathrooms = max(2, resident_count // 20)
    spaces.extend([
        ("Circulation Seating", corridor_seats, 3),
        ("Public Bathroom", public_bathrooms, 4.5)
    ])
    
    
    # Create DataFrame
    df = pd.DataFrame(spaces, columns=["Program Name", "Space Count Required", "Area per Space Required"])
    df["Color"] = df["Program Name"].map(SPACE_COLORS)
    
    return df

def save_space_program(home: RetirementHome, output_path: str):
    """Save space program to CSV file"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df = calculate_space_requirements(home)
    df.to_csv(output_path, index=False)
    return df

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
    
    # Generate and save space program
    output_path = f"output/space_program_v{version}.csv"
    space_program = save_space_program(retirement_home, output_path)
    print(f"\nSpace program saved to: {output_path}")
    
    return retirement_home