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

Backend:
- Python
- Flask
- SQLAlchemy with GeoAlchemy2

Database:
- PostgreSQL
- PostGIS

Infrastructure:

#### 3.1.2 Data Flow
User inputs → Components → Store actions
Store actions → State updates
State updates → Component re-renders
Components → API calls through services
Services → Backend API responses → State updates
State updates → Component re-renders

### 3.1.3 Project Structure

```
archestra/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── api/
│   │   └── services/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── stores/
│   │   └── views/
│   ├── public/
│   ├── package.json
│   └── vite.config.js    # Vue build configuration
│
├── .gitignore
├── README.md
└── docker-compose.yml    # Optional, for containerization
```

### 3.2 Frontend Architecture

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


#### 3.2.4 API Integration

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

### 3.3 Backend Architecture

#### 3.3.2 Backend Components
- **app/**: The main application directory containing all components of the backend.
  - **__init__.py**: The app factory that initializes the Flask application.
  - **models/**: Contains SQLAlchemy models that define the database structure.
    - **__init__.py**: Initializes the models package.
    - **plot.py**: Defines the Plot model, including PostGIS columns for geographical data.
    - **district.py**: Defines the District model, also with PostGIS columns.
    - **household.py**: Contains the Household preferences model.
    - **cooperative.py**: Manages associations between plots and households.
  - **api/**: Contains Flask Blueprints for organizing API endpoints.
    - **__init__.py**: Initializes the API package.
    - **preferences.py**: Endpoints for managing household preferences.
    - **plots.py**: Endpoints for searching plots based on user criteria.
    - **districts.py**: Endpoints for accessing district data.
  - **services/**: Contains business logic and algorithms.
    - **__init__.py**: Initializes the services package.
    - **matching.py**: Implements the plot matching algorithm.
    - **calculator.py**: Handles cost calculations based on user inputs.
- **config.py**: Configuration settings for the application.
- **run.py**: The entry point for running the application.

#### 3.3.3 App factory pattern
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_object="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Needed for Vue.js frontend
    
    # Register blueprints
    from app.api import preferences, plots, districts
    app.register_blueprint(preferences.bp)
    app.register_blueprint(plots.bp)
    app.register_blueprint(districts.bp)
    
    return app
```
