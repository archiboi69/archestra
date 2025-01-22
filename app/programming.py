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
    
    # Calculate office spaces by department and total staff
    for dept_name, positions in departments.items():
        for position, details in positions.items():
            current_count = details["count"]
            office_type = details["type"]
            area = OFFICE_STANDARDS[office_type]
            total_staff += current_count  # Add to total staff count
            
            # Define standard dimensions based on office type
            dimensions = {
                "A": {"width": 5.0, "depth": 5.0},  # Executive 25m²
                "B": {"width": 5.0, "depth": 3.0},  # Senior manager 15m²
                "C": {"width": 4.0, "depth": 3.0},  # Manager 12m²
                "D": {"width": 3.2, "depth": 2.5},  # Standard enclosed 8m²
                "E": {"width": 3.0, "depth": 2.0}   # Open plan 6m²
            }
            
            spaces.append({
                "Department": dept_name,
                "Program Name": position,
                "Space Count": current_count,
                "Area per Space": area,
                "Width": dimensions[office_type]["width"],
                "Depth": dimensions[office_type]["depth"],
                "Color": "#FFE4B5"  # Standard office color
            })

    # Calculate support spaces based on total staff
    for space_name, specs in SUPPORT_SPACES.items():
        if "ratio" in specs:
            count = max(1, int(total_staff * specs["ratio"]))
        else:
            count = specs["count"]
            
        # Define dimensions for support spaces where relevant
        support_dimensions = {
            "Board Room": {"width": 8.0, "depth": 6.25},
            "Board Room Ante Room": {"width": 5.0, "depth": 3.0},
            "Board Room Private Toilet": {"width": 2.25, "depth": 2.0},
            "Board Room Pantry": {"width": 4.0, "depth": 2.0},
            "Conference Room Large": {"width": 6.0, "depth": 5.0},
            "Conference Room Small": {"width": 5.0, "depth": 4.0},
            "Copy Rooms": {"width": 5.0, "depth": 3.0},
            "Server Room": {"width": 5.0, "depth": 4.0}
        }
        
        space_data = {
            "Department": "Support",
            "Program Name": space_name,
            "Space Count": count,
            "Area per Space": specs["area"],
            "Color": "#E6E6FA"  # Light support space color
        }
        
        # Add dimensions if available
        if space_name in support_dimensions:
            space_data["Width"] = support_dimensions[space_name]["width"]
            space_data["Depth"] = support_dimensions[space_name]["depth"]
            
        spaces.append(space_data)

    # Add special uses
    for space_name, quantity in special_uses.items():
        if quantity["current"] > 0:
            # Define dimensions for special spaces
            special_dimensions = {
                "Training Room": {"width": 8.0, "depth": 5.0},
                "Conference Center": {"width": 10.0, "depth": 10.0},
                "Gym": {"width": 10.0, "depth": 8.0},
                "Cafeteria": {"width": 12.0, "depth": 10.0},
                "Archive": {"width": 6.0, "depth": 5.0}
            }
            
            space_data = {
                "Department": "Special",
                "Program Name": space_name,
                "Space Count": quantity["current"],
                "Area per Space": SPECIAL_USES[space_name]["area"],
                "Color": "#98FB98"  # Light green for special spaces
            }
            
            # Add dimensions if available
            if space_name in special_dimensions:
                space_data["Width"] = special_dimensions[space_name]["width"]
                space_data["Depth"] = special_dimensions[space_name]["depth"]
                
            spaces.append(space_data)

    # Create DataFrame without circulation
    df = pd.DataFrame(spaces)
    
    # Calculate total areas
    df['Total Area'] = df['Space Count'] * df['Area per Space']
    
    return df

def save_space_program(df, output_path):
    """Save space program to CSV file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Ensure columns are in the desired order
    columns = ["Department", "Program Name", "Space Count", "Area per Space", "Color"]
    if "Width" in df.columns:
        columns.extend(["Width", "Depth"])
    
    df = df[columns]
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
    net_area = space_program['Total Area'].sum()
    circulation_area = net_area * 0.4  # 40% circulation
    total_gfa = net_area + circulation_area
    
    print(f"\nNet Area: {net_area:.1f}m²")
    print(f"Circulation Area (40%): {circulation_area:.1f}m²")
    print(f"Total GFA: {total_gfa:.1f}m²")
    
    return {
        "version": version,
        "current_gfa": total_gfa,
        "projected_gfa": total_gfa * 1.15,  # Adding 15% for future growth
        "space_program": space_program
    }