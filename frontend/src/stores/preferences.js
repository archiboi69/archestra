import { defineStore } from 'pinia'

export const usePreferencesStore = defineStore('preferences', {
    state: () => ({
        spaces: {
            singleBedrooms: 0,
            doubleBedrooms: 0,
            bathrooms: 1,
            wc: 0,
            kitchen: 'kitchenette'
        
        },
        // Areas in square meters
        areaConstants: {
            singleBedroom: 10.0,
            doubleBedroom: 12.0,
            bathroom: 4.5,
            wc: 1.6,
            kitchen: 8.0,
            kitchenette: 4.2,
            livingRoom: 20.0
        }
}),
    getters: {
        totalArea: (state) => {
            const usableArea = (
                state.spaces.singleBedrooms * state.areaConstants.singleBedroom +
                state.spaces.doubleBedrooms * state.areaConstants.doubleBedroom +
                state.spaces.bathrooms * state.areaConstants.bathroom +
                state.spaces.wc * state.areaConstants.wc +
                (state.spaces.kitchen === 'kitchenette' ? state.areaConstants.kitchenette : state.areaConstants.kitchen) +
                state.areaConstants.livingRoom)
            
            // Add 10% for circulation/walls and round to 2 decimal places
            return (usableArea / 0.9).toFixed(0)
        }
    },
    actions: {
        updateSpaces(newSpaces) {
            this.spaces = newSpaces
        }
    }
})