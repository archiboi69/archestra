<template>
    <div class="space-y-6">
        <!-- Double Bedrooms -->
        <Card>
            <CardHeader>
                <CardTitle>Sypialnie dwuosobowe</CardTitle>
            </CardHeader>
            <CardContent>
                <!-- Count Selection -->
                <ToggleGroup 
                    type="single" 
                    v-model="preferencesStore.spaces.doubleBedroom.count"
                    class="justify-start mb-4"
                >
                    <ToggleGroupItem 
                        v-for="n in 5" 
                        :key="n" 
                        :value="n.toString()"
                        class="px-4 py-2"
                    >
                        {{ n }}
                    </ToggleGroupItem>
                </ToggleGroup>

                <!-- Size Selection (only shown if count > 0) -->
                <RadioGroup 
                    v-if="parseInt(preferencesStore.spaces.doubleBedroom.count) > 0"
                    v-model="preferencesStore.spaces.doubleBedroom.size"
                >
                    <div class="grid grid-cols-3 gap-4">
                        <div v-for="(size, key) in roomSizes.doubleBedroom" :key="key"
                            class="flex flex-col items-center p-4 rounded-lg border cursor-pointer data-[state=checked]:border-primary"
                        >
                            <RadioGroupItem :value="key" class="sr-only" />
                            <span class="font-medium">{{ size.label }}</span>
                            <span class="text-sm text-muted-foreground">{{ size.area }}m²</span>
                        </div>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>

        <!-- Bathrooms (always at least 1) -->
        <Card>
            <CardHeader>
                <CardTitle>Łazienki</CardTitle>
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

                <RadioGroup v-model="preferencesStore.spaces.bathroom.size">
                    <div class="grid grid-cols-3 gap-4">
                        <div v-for="(size, key) in roomSizes.bathroom" :key="key"
                            class="flex flex-col items-center p-4 rounded-lg border cursor-pointer data-[state=checked]:border-primary"
                        >
                            <RadioGroupItem :value="key" class="sr-only" />
                            <span class="font-medium">{{ size.label }}</span>
                            <span class="text-sm text-muted-foreground">{{ size.area }}m²</span>
                        </div>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>
    </div>
</template>

<script setup>
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { usePreferencesStore } from '@/stores/preferences'

const preferencesStore = usePreferencesStore()

const roomSizes = {
    doubleBedroom: {
        compact: { label: 'Kompaktowa', area: 12 },
        standard: { label: 'Standardowa', area: 14 },
        spacious: { label: 'Przestronna', area: 16 }
    },
    singleBedroom: {
        compact: { label: 'Kompaktowa', area: 8 },
        standard: { label: 'Standardowa', area: 10 },
        spacious: { label: 'Przestronna', area: 12 }
    },
    bathroom: {
        compact: { label: 'Kompaktowa', area: 4 },
        standard: { label: 'Standardowa', area: 6 },
        spacious: { label: 'Przestronna', area: 8 }
    }
}
</script>

<style>
</style>