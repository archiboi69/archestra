import { defineStore } from 'pinia'

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
        }
    }),
    getters: {
        totalArea: (state) => {
            const usableArea = Object.entries(state.spaces).reduce((total, [roomType, room]) => {
                const count = room.count ? parseInt(room.count) : 1;
                return total + (state.areaConstants[roomType][room.size] * count);
            }, 0);
            
            // Add 10% for circulation/walls and round to 0 decimal places
            return (usableArea / 0.9).toFixed(0);
        }
    },
    actions: {
        updateSpaces(newSpaces) {
            this.spaces = newSpaces
        }
    }
})