import { defineStore } from 'pinia'
import { districts } from '@/data/districts'

export const usePreferencesStore = defineStore('preferences', {
    state: () => ({
        spaces: {
            livingRoom: {
                size: 'standard'
            },
            doubleBedroom: {
                count: '0',
                size: 'standard'
            },
            singleBedroom: {
                count: '0',
                size: 'standard'
            },
            bathroom: {
                count: '1',
                size: 'standard'
            },
            kitchen: {
                type: 'kitchenette',
                size: 'standard'
            },
            wc: {
                count: '0'
            }
        },
        amenities: {
            commonAreaFinish: 'standard',
            elevator: false,
            laundry: false,
            workshop: false,
            lounge: false,
            fitness: false,
            sauna: false
        },
        pricesConstants: {
            commonAreaFinish: {
                economy: 5100,
                standard: 5500,
                premium: 6200
            },
            elevator: 20000,
            laundry: 10000,
            workshop: 10000,
            lounge: 10000,
            fitness: 10000,
            sauna: 10000,
        },
        areaConstants: {
            livingRoom: {
                compact: 16,
                standard: 20,
                spacious: 24
            },
            doubleBedroom: {
                compact: 10,
                standard: 12,
                spacious: 16
            },
            singleBedroom: {
                compact: 8,
                standard: 10,
                spacious: 14
            },
            bathroom: {
                compact: 3.5,
                standard: 4.5,
                spacious: 8
            },
            kitchen: {
                kitchenette: {
                    compact: 4,
                    standard: 5,
                    spacious: 6
                },
                separate: {
                    compact: 6,
                    standard: 8,
                    spacious: 10
                }
            },
            wc: 1.5
        },
        location: {
            selectedDistricts: [],  // Array of district IDs
            selectedPlot: null      // Move selectedPlot inside location
        },
        districtsConstants: {
            mokotow: {
                name: 'Mokotów',
                landPrice: 3000,  // Price per m²
                coordinates: [
                    [52.193, 21.027],
                    // ... polygon points
                ]
            },
            // ... other districts
        },
    }),
    getters: {
        usableArea: (state) => {
            let area = 0

            // Living Room
            area += state.areaConstants.livingRoom[state.spaces.livingRoom.size]

            // Kitchen (based on type)
            area += state.areaConstants.kitchen[state.spaces.kitchen.type][state.spaces.kitchen.size]

            // Double Bedrooms
            const doubleBedCount = parseInt(state.spaces.doubleBedroom.count)
            if (doubleBedCount > 0) {
                area += doubleBedCount * state.areaConstants.doubleBedroom[state.spaces.doubleBedroom.size]
            }

            // Single Bedrooms
            const singleBedCount = parseInt(state.spaces.singleBedroom.count)
            if (singleBedCount > 0) {
                area += singleBedCount * state.areaConstants.singleBedroom[state.spaces.singleBedroom.size]
            }

            // Bathrooms
            const bathroomCount = parseInt(state.spaces.bathroom.count)
            area += bathroomCount * state.areaConstants.bathroom[state.spaces.bathroom.size]

            // WC
            const wcCount = parseInt(state.spaces.wc.count)
            if (wcCount > 0) {
                area += wcCount * state.areaConstants.wc
            }

            return area
        },
        totalArea: (state) => {
            // Add 10% for circulation/walls and round to 0 decimal places
            return Math.round(state.usableArea / 0.9)
        },
        commonAreaShare: (state) => {
            // Share of the common area is 25% of the total area and rounded to 2 decimal places
            return state.totalArea / 3
        },
        availableDistricts: () => districts.features,
        selectedDistrictDetails: (state) => 
            districts.features.filter(d => 
                state.location.selectedDistricts.includes(d.properties.id)
            )
    },
    actions: {
        updateSpaces(newSpaces) {
            this.spaces = newSpaces
        },
        toggleAmenity(name) {
            this.amenities[name] = !this.amenities[name]
        },
        toggleDistrict(districtId) {
            const idx = this.location.selectedDistricts.indexOf(districtId)
            if (idx === -1) {
                this.location.selectedDistricts.push(districtId)
            } else {
                this.location.selectedDistricts.splice(idx, 1)
            }
        },
        selectPlot(plot) {
            this.location.selectedPlot = plot  // Update to use location.selectedPlot
            console.log('Store updated with plot:', plot)
        }
    }
})