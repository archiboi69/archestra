<template>
    <div class="space-y-6">
        

        <!-- Living Room -->
         <Card>
            <CardHeader>
                <CardTitle>Pokój dzienny</CardTitle>
            </CardHeader>
            <CardContent>
                <!-- Size Selection -->
                 <RadioGroup
                    v-model="preferencesStore.spaces.livingRoom.size"
                    class="space-y-2"
                    >
                    <div v-for="(size, key) in roomSizes.livingRoom" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`lr-${key}`" :value="key" />
                        <label :for="`lr-${key}`" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {{ size.label }} ({{ size.area }}m²)
                        </label>
                    </div> 
                </RadioGroup>
            </CardContent>
         </Card>
         
        <!-- Kitchen -->
        <Card>
            <CardHeader>
                <CardTitle>Kuchnia</CardTitle>
            </CardHeader>
            <CardContent>
                <!-- Type Selection -->
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.kitchen.type"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        value="kitchenette"
                        class="px-4 py-2"
                    >
                        Aneks kuchenny
                    </ToggleGroupItem>
                    <ToggleGroupItem 
                        value="separate"
                        class="px-4 py-2"
                    >
                        Oddzielna kuchnia
                    </ToggleGroupItem>
                </ToggleGroup>

                <!-- Size Selection -->
                <RadioGroup 
                    v-model="preferencesStore.spaces.kitchen.size"
                    class="space-y-2"
                >
                    <div v-for="(size, key) in getKitchenSizes" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`kitchen-${key}`" :value="key" />
                        <label :for="`kitchen-${key}`" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {{ size.label }} ({{ size.area }}m²)
                        </label>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>

        <!-- Double Bedrooms -->
        <Card>
            <CardHeader>
                <CardTitle>Sypialnia dwuosobowa</CardTitle>
            </CardHeader>
            <CardContent>
                <!-- Count Selection -->
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.doubleBedroom.count"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        v-for="n in 6" 
                        :key="n-1" 
                        :value="(n-1).toString()"
                        class="px-4 py-2"
                    >
                        {{ n-1 }}
                    </ToggleGroupItem>
                </ToggleGroup>

                <!-- Size Selection (only shown if count > 0) -->
                <RadioGroup 
                    v-if="parseInt(preferencesStore.spaces.doubleBedroom.count) > 0"
                    v-model="preferencesStore.spaces.doubleBedroom.size"
                    class="space-y-2"
                >
                    <div v-for="(size, key) in roomSizes.doubleBedroom" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`db-${key}`" :value="key" />
                        <label :for="`db-${key}`" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {{ size.label }} ({{ size.area }}m²)
                        </label>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>

        <!-- Single Bedroom -->
        <Card>
            <CardHeader>
                <CardTitle>Sypialnia jednoosobowa</CardTitle>
            </CardHeader>
            <CardContent>
                <!-- Count Selection -->
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.singleBedroom.count"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        v-for="n in 6" 
                        :key="n-1" 
                        :value="(n-1).toString()"
                        class="px-4 py-2"
                    >
                        {{ n-1 }}
                    </ToggleGroupItem>
                </ToggleGroup>
                <!-- Size Selection (only shown if count > 0) -->
                <RadioGroup 
                    v-if="parseInt(preferencesStore.spaces.singleBedroom.count) > 0"
                    v-model="preferencesStore.spaces.singleBedroom.size"
                    class="space-y-2"
                >
                    <div v-for="(size, key) in roomSizes.singleBedroom" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`sb-${key}`" :value="key" />
                        <label :for="`sb-${key}`" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {{ size.label }} ({{ size.area }}m²)
                        </label>
                    </div>
                    
                </RadioGroup>
            </CardContent>
        </Card>

        <!-- Bathrooms -->
        <Card>
            <CardHeader>
                <CardTitle>Łazienka</CardTitle>
            </CardHeader>
            <CardContent>
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.bathroom.count"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        v-for="n in 3" 
                        :key="n" 
                        :value="n.toString()"
                        class="px-4 py-2"
                    >
                        {{ n }}
                    </ToggleGroupItem>
                </ToggleGroup>

                <RadioGroup 
                    v-model="preferencesStore.spaces.bathroom.size"
                    class="space-y-2"
                >
                    <div v-for="(size, key) in roomSizes.bathroom" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`bath-${key}`" :value="key" />
                        <label :for="`bath-${key}`" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            {{ size.label }} ({{ size.area }}m²)
                        </label>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>
        <Card>
            <CardHeader>
                <CardTitle>WC</CardTitle>
            </CardHeader>
            <CardContent>
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.wc.count"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        v-for="n in 4" 
                        :key="n-1" 
                        :value="(n-1).toString()"
                        class="px-4 py-2"
                    >
                        {{ n-1 }}
                    </ToggleGroupItem>
                </ToggleGroup>
            </CardContent>
        </Card>
    </div>
</template>

<script setup>
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group/index.js'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card/index.js'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group/index.js'
import { usePreferencesStore } from '@/stores/preferences'
import { computed } from 'vue'

console.log('SpaceSelector mounted')

const preferencesStore = usePreferencesStore()
console.log('Store:', preferencesStore.spaces)

const roomSizes = {
    livingRoom: {
        compact: { 
            label: 'Kompaktowy', 
            area: preferencesStore.areaConstants.livingRoom.compact 
        },
        standard: { 
            label: 'Standardowy', 
            area: preferencesStore.areaConstants.livingRoom.standard 
        },
        spacious: { 
            label: 'Przestronny', 
            area: preferencesStore.areaConstants.livingRoom.spacious 
        }
    },
    doubleBedroom: {
        compact: { 
            label: 'Kompaktowa', 
            area: preferencesStore.areaConstants.doubleBedroom.compact 
        },
        standard: { 
            label: 'Standardowa', 
            area: preferencesStore.areaConstants.doubleBedroom.standard 
        },
        spacious: { 
            label: 'Przestronna', 
            area: preferencesStore.areaConstants.doubleBedroom.spacious 
        }
    },
    singleBedroom: {
        compact: { 
            label: 'Kompaktowa', 
            area: preferencesStore.areaConstants.singleBedroom.compact 
        },
        standard: { 
            label: 'Standardowa', 
            area: preferencesStore.areaConstants.singleBedroom.standard 
        },
        spacious: { 
            label: 'Przestronna', 
            area: preferencesStore.areaConstants.singleBedroom.spacious 
        }
    },
    bathroom: {
        compact: { 
            label: 'Kompaktowa', 
            area: preferencesStore.areaConstants.bathroom.compact 
        },
        standard: { 
            label: 'Standardowa', 
            area: preferencesStore.areaConstants.bathroom.standard 
        },
        spacious: { 
            label: 'Przestronna', 
            area: preferencesStore.areaConstants.bathroom.spacious 
        }
    },
    kitchen: {
        kitchenette: {
            compact: { 
                label: 'Kompaktowy', 
                area: preferencesStore.areaConstants.kitchen.kitchenette.compact 
            },
            standard: { 
                label: 'Standardowy', 
                area: preferencesStore.areaConstants.kitchen.kitchenette.standard 
            },
            spacious: { 
                label: 'Przestronny', 
                area: preferencesStore.areaConstants.kitchen.kitchenette.spacious 
            }
        },
        separate: {
            compact: { 
                label: 'Kompaktowa', 
                area: preferencesStore.areaConstants.kitchen.separate.compact 
            },
            standard: { 
                label: 'Standardowa', 
                area: preferencesStore.areaConstants.kitchen.separate.standard 
            },
            spacious: { 
                label: 'Przestronna', 
                area: preferencesStore.areaConstants.kitchen.separate.spacious 
            }
        }
    },
    wc: {
        area: preferencesStore.areaConstants.wc
    }
}

// Computed property to get the correct kitchen sizes based on type
const getKitchenSizes = computed(() => {
    return roomSizes.kitchen[preferencesStore.spaces.kitchen.type]
})
</script>

<style>
</style>