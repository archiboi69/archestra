from app.models import RetirementHome

DEFAULTS = {
    "coverage_ratio": 0.3,         # Building footprint / Plot area
    "sqm_per_resident": 70,        # Total GFA per resident including all spaces
    "stories": 3                   # Default number of stories (will be updated per site)
}

VALID_RANGES = {
    "resident_count": (1, 300),     # Total number of residents - wide range for validation
    "coverage_ratio": (0.15, 0.4)   # Min and max coverage ratios for initial estimates
}


def get_inputs():
    print("\n=== Retirement Home Programming Calculator ===")
    
    # Version tracking
    version = input("Version number: ")
    
    # Get resident range
    while True:
        try:
            min_residents = int(input(
                f"Minimum number of residents ({VALID_RANGES['resident_count'][0]}-{VALID_RANGES['resident_count'][1]}): "
            ))
            max_residents = int(input(
                f"Maximum number of residents ({VALID_RANGES['resident_count'][0]}-{VALID_RANGES['resident_count'][1]}): "
            ))
            
            # Validate inputs
            if (VALID_RANGES['resident_count'][0] <= min_residents <= VALID_RANGES['resident_count'][1] and
                VALID_RANGES['resident_count'][0] <= max_residents <= VALID_RANGES['resident_count'][1] and
                min_residents <= max_residents):
                break
            print("Invalid range! Make sure min ≤ max and both are within valid limits.")
        except ValueError:
            print("Please enter numbers!")
    
    retirement_home = RetirementHome(
        version=version,
        min_residents=min_residents,
        max_residents=max_residents
    )
    return retirement_home