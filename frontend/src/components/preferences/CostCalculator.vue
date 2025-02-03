<script setup>
import { usePreferencesStore } from '@/stores/preferences'
import { computed } from 'vue'
import { Card, CardContent, CardTitle, CardDescription, CardHeader } from '@/components/ui/card'

const preferencesStore = usePreferencesStore()

const totalArea = computed(() => preferencesStore.totalArea)
const commonArea = computed(() => preferencesStore.commonArea)

const roomCount = computed(() => {
    const singleBeds = parseInt(preferencesStore.spaces.singleBedroom.count)
    const doubleBeds = parseInt(preferencesStore.spaces.doubleBedroom.count)
    return singleBeds + doubleBeds + 1 // +1 for living room
})

const apartmentType = computed(() => {
    const count = roomCount.value
    if (count === 1) return 'Kawalerka'
    if (count === 2) return 'Mieszkanie dwupokojowe'
    if (count === 3) return 'Mieszkanie trzypokojowe'
    if (count === 4) return 'Mieszkanie czteropokojowe'
    return `Mieszkanie ${count}-pokojowe`
})

const COST_PER_SQM = {
    construction: 5100,
    land: 3000
}

const amenitiesCost = computed(() => {
    // Required common areas cost based on finish standard
    const commonAreaCost = preferencesStore.pricesConstants.commonAreaFinish[preferencesStore.amenities.commonAreaFinish] 
        * preferencesStore.commonAreaShare

    // Optional amenities (elevator, laundry, etc.)
    const optionalAmenitiesCost = Object.entries(preferencesStore.amenities)
        .filter(([name, enabled]) => name !== 'commonAreaFinish' && enabled)
        .reduce((total, [name]) => total + preferencesStore.pricesConstants[name], 0)

    return commonAreaCost + optionalAmenitiesCost
})

const constructionCostPerSqm = computed(() => COST_PER_SQM.construction)
const amenitiesCostPerSqm = computed(() => amenitiesCost.value / totalArea.value)

// Calculate average land price from selected districts
const landCostPerSqm = computed(() => {
    const selectedDistricts = preferencesStore.selectedDistrictDetails
    
    if (selectedDistricts.length === 0) {
        // Default price when no district selected
        return 2800 // Average price as fallback
    }

    // Calculate average price from selected districts
    const totalPrice = selectedDistricts.reduce((sum, district) => 
        sum + district.properties.landPrice, 0
    )
    return Math.round(totalPrice / selectedDistricts.length)
})

const totalCostPerSqm = computed(() => 
    constructionCostPerSqm.value + 
    amenitiesCostPerSqm.value + 
    landCostPerSqm.value
)

const totalCost = computed(() => totalArea.value * totalCostPerSqm.value)

const formatCurrency = (value) => {
    return value.toLocaleString('pl-PL', { 
        style: 'currency', 
        currency: 'PLN',
        maximumFractionDigits: 0
    })
}

const formatPrice = (value) => {
    return value.toLocaleString('pl-PL', { 
        style: 'decimal',
        maximumFractionDigits: 0
    }) + ' zł'
}
</script>

<template>
    <Card class="fixed bottom-4 right-4 w-96 shadow-lg bg-background/95 backdrop-blur">
        <CardHeader>
            <CardTitle>{{ apartmentType }}</CardTitle>
            <CardDescription>
                Powierzchnia użytkowa {{ totalArea }} m²
                <!-- Add selected districts info -->
                <div v-if="preferencesStore.selectedDistrictDetails.length > 0" class="mt-1">
                    {{ preferencesStore.selectedDistrictDetails.map(d => d.properties.name).join(', ') }}
                </div>
            </CardDescription>
        </CardHeader>
        <CardContent class="space-y-3">
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span>Stan deweloperski</span>
                    <span class="font-medium">{{ formatPrice(constructionCostPerSqm) }} /m²</span>
                </div>
                <div class="flex justify-between">
                    <span>Części wspólne</span>
                    <span class="font-medium">{{ formatPrice(amenitiesCostPerSqm) }} /m²</span>
                </div>
                <div class="flex justify-between">
                    <span>Zakup gruntu</span>
                    <span class="font-medium">{{ formatPrice(landCostPerSqm) }} /m²</span>
                </div>
                <div class="flex justify-between pt-2 border-t">
                    <span>Całkowity koszt m²</span>
                    <span class="font-medium">{{ formatPrice(totalCostPerSqm) }} /m²</span>
                </div>
            </div>
            <div class="flex justify-between pt-2 border-t text-lg font-medium">
                <span>Koszt mieszkania</span>
                <span>{{ formatCurrency(totalCost) }}</span>
            </div>
        </CardContent>
    </Card>
</template>

