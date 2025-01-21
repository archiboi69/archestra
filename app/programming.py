import pandas as pd
import os

# Office space standards (m²)
OFFICE_STANDARDS = {
    "A": 25.0,  # Executive office
    "B": 15.0,  # Senior manager office
    "C": 12.0,  # Manager office
    "D": 8.0,   # Standard enclosed office
    "E": 6.0    # Open plan workstation
}

# Updated default department structure based on notepad
DEFAULT_DEPARTMENTS = {
    "Executive": {
        "CEO": {"type": "A", "count": 1, "projected_growth": 0},
        "CEO Admin Assistant": {"type": "D", "count": 1, "projected_growth": 0},
        "President": {"type": "A", "count": 1, "projected_growth": 0},
        "President Admin Assistant": {"type": "D", "count": 1, "projected_growth": 0},
        "CFO": {"type": "A", "count": 1, "projected_growth": 0},
        "CFO Admin Assistant": {"type": "D", "count": 1, "projected_growth": 0}
    },
    "Finance": {
        "VP Finance": {"type": "B", "count": 1, "projected_growth": 0},
        "Director of Finance": {"type": "B", "count": 1, "projected_growth": 0},
        "Accountants": {"type": "E", "count": 4, "projected_growth": 2}
    },
    "Marketing": {
        "VP Marketing": {"type": "B", "count": 1, "projected_growth": 0},
        "Administrative Assistant": {"type": "D", "count": 1, "projected_growth": 0},
        "Analysts": {"type": "E", "count": 3, "projected_growth": 2},
        "Product Leaders": {"type": "C", "count": 2, "projected_growth": 1}
    },
    "Real Estate": {
        "VP Real Estate": {"type": "B", "count": 1, "projected_growth": 0},
        "Administrative Assistant": {"type": "D", "count": 1, "projected_growth": 0},
        "Leasing Coordinators": {"type": "C", "count": 2, "projected_growth": 1},
        "Lease Administration": {"type": "E", "count": 2, "projected_growth": 1}
    },
    "Planning": {
        "VP Planning and Design": {"type": "B", "count": 1, "projected_growth": 0},
        "Sr. Project Manager": {"type": "C", "count": 1, "projected_growth": 1},
        "Project Managers": {"type": "C", "count": 2, "projected_growth": 2},
        "Designers": {"type": "E", "count": 4, "projected_growth": 2}
    },
    "IT": {
        "VP IT": {"type": "B", "count": 1, "projected_growth": 0},
        "Sr. Programmer": {"type": "C", "count": 1, "projected_growth": 1},
        "Programmers": {"type": "E", "count": 3, "projected_growth": 2},
        "Consultants": {"type": "E", "count": 2, "projected_growth": 1}
    },
    "Front Office": {
        "Receptionist": {"type": "D", "count": 1, "projected_growth": 0}
    }
}

# Updated support spaces standards
SUPPORT_SPACES = {
    "Board Room": {"area": 50.0, "count": 1},        # Seating 16
    "Board Room Ante Room": {"area": 15.0, "count": 1},
    "Board Room Private Toilet": {"area": 4.5, "count": 1},
    "Board Room Pantry": {"area": 8.0, "count": 1},
    "Conference Room Large": {"area": 30.0, "ratio": 0.04},  # 10-12 people
    "Conference Room Small": {"area": 20.0, "ratio": 0.06},  # 6-8 people
    "Lunchroom": {"area": 80.0, "count": 1},
    "Copy Rooms": {"area": 15.0, "ratio": 0.05},     # One per 20 people
    "Receiving Area": {"area": 20.0, "count": 1},
    "File Room/Fireproof": {"area": 30.0, "count": 1},
    "Library": {"area": 25.0, "count": 1},
    "Server Room": {"area": 20.0, "count": 1},
    "Satellite Pantry": {"area": 12.0, "ratio": 0.04},
    "Visitor Coats": {"area": 8.0, "count": 1},
    "Staff Coats": {"area": 0.5, "ratio": 1.0},      # 0.5m² per person
    "Restrooms": {"area": 25.0, "ratio": 0.04}       # One per 25 people
}

# Special uses that can be added (keeping this for flexibility)
SPECIAL_USES = {
    "Training Room": {"area": 40.0},
    "Conference Center": {"area": 100.0},
    "Gym": {"area": 80.0},
    "Cafeteria": {"area": 120.0},
    "Archive": {"area": 30.0}
}

def calculate_space_requirements(departments, special_uses):
    """Calculate detailed space requirements based on department data and special uses"""
    spaces = []
    total_staff = 0
    
    # Calculate office spaces by department
    for dept_name, positions in departments.items():
        for position, details in positions.items():
            current_count = details["count"]
            future_count = current_count + details["projected_growth"]
            office_type = details["type"]
            area = OFFICE_STANDARDS[office_type]
            
            spaces.append({
                "Program Name": f"{dept_name} - {position}",
                "Space Count Current": current_count,
                "Space Count Projected": future_count,
                "Area per Space": area,
                "Total Area Current": current_count * area,
                "Total Area Projected": future_count * area,
                "Space Type": "Office"
            })
            total_staff += future_count

    # Calculate support spaces
    for space_name, specs in SUPPORT_SPACES.items():
        if "ratio" in specs:
            count = max(1, int(total_staff * specs["ratio"]))
        else:
            count = specs["count"]
            
        spaces.append({
            "Program Name": space_name,
            "Space Count Current": count,
            "Space Count Projected": count,
            "Area per Space": specs["area"],
            "Total Area Current": count * specs["area"],
            "Total Area Projected": count * specs["area"],
            "Space Type": "Support"
        })

    # Add special uses
    for space_name, quantity in special_uses.items():
        if quantity["current"] > 0 or quantity["projected"] > 0:
            spaces.append({
                "Program Name": space_name,
                "Space Count Current": quantity["current"],
                "Space Count Projected": quantity["projected"],
                "Area per Space": SPECIAL_USES[space_name]["area"],
                "Total Area Current": quantity["current"] * SPECIAL_USES[space_name]["area"],
                "Total Area Projected": quantity["projected"] * SPECIAL_USES[space_name]["area"],
                "Space Type": "Special"
            })

    return pd.DataFrame(spaces)

def save_space_program(df, output_path):
    """Save space program to CSV file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

def get_inputs():
    print("\n=== Office Building Programming Calculator ===")
    
    # Version tracking
    version = input("Version number: ")
    
    departments = DEFAULT_DEPARTMENTS.copy()
    use_defaults = input("\nUse default department structure? (y/n): ").lower() == 'y'
    
    if not use_defaults:
        departments = {}
        while True:
            dept_name = input("\nEnter department name (or 'done' to finish): ")
            if dept_name.lower() == 'done':
                break
                
            departments[dept_name] = {}
            while True:
                position = input("Enter position title (or 'done' for next department): ")
                if position.lower() == 'done':
                    break
                    
                office_type = input(f"Office type (A-E) [A:{OFFICE_STANDARDS['A']}m², B:{OFFICE_STANDARDS['B']}m², C:{OFFICE_STANDARDS['C']}m², D:{OFFICE_STANDARDS['D']}m², E:{OFFICE_STANDARDS['E']}m²]: ").upper()
                while office_type not in OFFICE_STANDARDS:
                    print("Invalid office type!")
                    office_type = input("Office type (A-E): ").upper()
                
                current_count = int(input("Current number of positions: "))
                growth = int(input("Projected 10-year growth: "))
                
                departments[dept_name][position] = {
                    "type": office_type,
                    "count": current_count,
                    "projected_growth": growth
                }

    # Special uses
    special_uses = {}
    print("\nSpecial Uses Available:")
    for use, details in SPECIAL_USES.items():
        print(f"{use}: {details['area']}m²")
    
    while True:
        use = input("\nAdd special use (or 'done' to finish): ")
        if use.lower() == 'done':
            break
        if use in SPECIAL_USES:
            current = int(input("Current quantity: "))
            projected = int(input("Projected quantity: "))
            special_uses[use] = {"current": current, "projected": projected}
        else:
            print("Invalid special use!")

    # Calculate and save space program
    output_path = f"output/space_program_v{version}.csv"
    space_program = calculate_space_requirements(departments, special_uses)
    save_space_program(space_program, output_path)
    
    print(f"\nSpace program saved to: {output_path}")
    
    # Summary statistics
    current_total = space_program["Total Area Current"].sum()
    projected_total = space_program["Total Area Projected"].sum()
    
    print(f"\nTotal Current GFA: {current_total:.1f}m²")
    print(f"Total Projected GFA: {projected_total:.1f}m²")
    
    return {
        "version": version,
        "current_gfa": current_total,
        "projected_gfa": projected_total,
        "space_program": space_program
    }