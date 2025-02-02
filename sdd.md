# Archestra - Software Design Document

# 1. Introduction
## 1.1 Purpose
- Document the technical design of Archestra platform
- Serve as a reference for developers and future maintenance
- Define system architecture and component interactions

## 1.2 Scope
- Web application for matching households with municipal plots
- Cost calculation system for construction and land
- Cooperative formation platform

# 2. System Overview
## 2.1 Business Context
- Housing market problem in Poland
- Role of housing cooperatives
- Municipal land opportunities
- Target users (households looking for cooperative housing)

## 2.2 Key Features
- Preferences Collection
- Space requirements
- Amenity selection
- Budget calculation
- District Selection
- Interactive map
- Land cost visualization
- Plot Matching
- Municipal plot database
- Household-plot matching algorithm
- Cooperative list management

# 3. Architecture Design

## 3.1 High-Level Architecture

### 3.1.1 Technology Stack
Frontend:
- Vue.js 3 (Composition API)
- Tailwind CSS
- Leaflet.js (for maps)

Database & Backend Services:
- Prisma Postgres (for data storage)
- PostGIS capabilities
- Firebase/MongoDB Atlas (alternative options)

Infrastructure:
- Static hosting (Vercel)
- Serverless database
- Local data processing pipeline

### 3.1.2 Data Flow
1. Initial Data Processing:
   - Local Python scripts process GIS datasets
   - Pre-calculated values stored in database
   - Periodic updates through local pipeline

2. Runtime Data Flow:
   - User inputs → Components → Store actions
   - Store actions → Direct database queries
   - Database responses → State updates
   - State updates → Component re-renders

### 3.1.3 Project Structure
```
archestra/
├── data-pipeline/
│   ├── process.py        # GIS data processing
│   ├── upload.py         # Database upload scripts
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/    # Database interaction
│   │   ├── stores/
│   │   └── views/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

### 3.2 Frontend Architecture

#### 3.2.1 Database Integration

Example of a database service:
```javascript
// services/db.js
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export const db = {
  async getMatchingPlots(criteria) {
    return prisma.plots.findMany({
      where: {
        maxUnits: { gte: criteria.minUnits },
        district: { in: criteria.districts },
        // Spatial queries via PostGIS
      }
    })
  },
  
  async getPlotsByViewport(bounds) {
    return prisma.plots.findMany({
      where: {
        bbox: {
          // Viewport intersection query
        }
      },
      select: {
        id: true,
        center: true,
        properties: true
        // Exclude full geometry for performance
      }
    })
  }
}
```

#### 3.2.2 Data Processing Pipeline

Example of a data processing script:
```python
# data-pipeline/process.py
import geopandas as gpd
from sqlalchemy import create_engine

def process_and_upload():
    # Load and process GIS data
    gdf = gpd.read_file('raw_plots.geojson')
    
    # Pre-calculate important values
    gdf['buildable_area'] = calculate_buildable_area(gdf)
    gdf['estimated_min_units'] = estimate_min_units(gdf)
    gdf['estimated_max_units'] = estimate_max_units(gdf)
    
    # Add spatial indexes
    gdf['bbox'] = gdf.geometry.bounds
    gdf['center'] = gdf.geometry.centroid
    
    # Upload to database
    engine = create_engine(DATABASE_URL)
    gdf.to_postgis('plots', engine, if_exists='replace')
```

#### 3.2.2 Frontend Components

- **Components**: These are the building blocks of the user interface, responsible for rendering the UI and handling user interactions. They are organized into subdirectories based on their functionality:
  - **Preferences**: Contains components related to user preferences.
    - `SpaceSelector.vue`: Allows users to select space-related preferences.
    - `AmenitySelector.vue`: Lets users choose amenities they desire.
    - `CostCalculator.vue`: Calculates and displays the total cost based on user selections.
  - **Districts**: Contains components for district-related functionalities.
    - `DistrictMap.vue`: Displays a map of the selected districts.
    - `DistrictSelector.vue`: Enables users to select districts for their preferences.
  - **Matching**: Contains components that handle plot matching.
    - `PlotList.vue`: Displays a list of matching plots based on user preferences.
    - `PlotCard.vue`: Represents individual plot details in a card format.
    - `CooperativeJoin.vue`: Facilitates joining a cooperative for selected plots.

- **Services**: These are utility modules that handle business logic and API interactions.
  - `api.js`: Contains functions for making API calls to the backend.
  - `calculator.js`: Implements the logic for calculating costs based on user inputs.
  - `storage.js`: Manages local storage operations for persisting user data.

- **Stores**: These manage the application's state using a centralized store pattern.
  - `preferences.js`: Holds the state related to user preferences, such as spaces and amenities.
  - `matching.js`: Manages the state related to plot matching, including the list of matching plots.

- **Views**: These represent the different pages or screens in the application.
  - `PreferencesView.vue`: Displays the preferences selection interface.
  - `DistrictsView.vue`: Shows the district selection interface.
  - `MatchingView.vue`: Presents the results of the plot matching process.

### 3.2.4 API Integration

```javascript
// services/api.js
export const api = {
  async getMatchingPlots(preferences) {
    const response = await fetch('/api/plots/matching', {
      method: 'POST',
      body: JSON.stringify(preferences)
    })
    return response.json()
  },

  async joinCooperative(plotId) {
    const response = await fetch(`/api/plots/${plotId}/join`, {
      method: 'POST'
    })
    return response.json()
  }
}
```

#### 3.2.5 State Management

Archestra state might look like:
```javascript
{
    preferences: {
        spaces: {
            bedrooms: 2,
            bathrooms: 1,
            livingRoom: 30  // m2
        },
        amenities: {
            gym: true,
            garden: true
        }
    },
    costs: {
        construction: 600000,
        amenities: 50000,
        total: 650000
    },
    districts: {
        selected: ["Mokotow", "Wola"],
        landCosts: {
            "Mokotow": 200000,
            "Wola": 150000
        }
    },
    matchingPlots: [...]
}
```
A store might look like:
```javascript
// stores/preferences.js
import { defineStore } from 'pinia'

export const usePreferencesStore = defineStore('preferences', {
  // Central state
  state: () => ({
    spaces: {},
    amenities: {},
    districts: []
  }),

  // Computed values
  getters: {
    totalCost: (state) => {
      return calculateCost(state.spaces, state.amenities)
    },
    isWithinBudget: (state) => {
      return state.totalCost <= state.maxBudget
    }
  },

  // Methods to change state
  actions: {
    updateSpaces(spaces) {
      this.spaces = spaces
    },
    updateAmenities(amenities) {
      this.amenities = amenities
    }
  }
})
```

A component might look like:
```javascript
// components/preferences/SpaceSelector.vue
<template>
  <div>
    <input v-model="spaces.bedrooms">
    <p>Total Cost: {{ totalCost }}</p>
  </div>
</template>

<script setup>
import { usePreferencesStore } from '@/stores/preferences'

const store = usePreferencesStore()

// Access state directly
const spaces = store.spaces
const totalCost = store.totalCost

// Update state
function addBedroom() {
  store.updateSpaces({ ...spaces, bedrooms: spaces.bedrooms + 1 })
}
</script>
```

### 3.3 Performance Optimizations

#### 3.3.1 Data Loading
- Progressive loading based on viewport
- Simplified geometries for overview
- Full geometry loading on demand
- Client-side caching of viewed areas

#### 3.3.2 Calculations
- Pre-calculated values stored in database
- Complex calculations done in local pipeline
- Simple filtering and matching on client
- Web Workers for heavy client-side operations

#### 3.3.3 Cost Management
- Optimize data transfer sizes
- Cache frequently accessed data
- Monitor database usage metrics
- Implement usage limits if needed
