<script setup>
import { usePreferencesStore } from '@/stores/preferences'
import { computed } from 'vue'
import { Card, CardContent, CardTitle, CardDescription, CardHeader } from '@/components/ui/card'

const preferencesStore = usePreferencesStore()

const totalArea = computed(() => {
    let area = 0

    // Living Room
    area += preferencesStore.areaConstants.livingRoom[preferencesStore.spaces.livingRoom.size]

    // Kitchen (based on type)
    area += preferencesStore.areaConstants.kitchen[preferencesStore.spaces.kitchen.type][preferencesStore.spaces.kitchen.size]

    // Double Bedrooms
    const doubleBedCount = parseInt(preferencesStore.spaces.doubleBedroom.count)
    if (doubleBedCount > 0) {
        area += doubleBedCount * preferencesStore.areaConstants.doubleBedroom[preferencesStore.spaces.doubleBedroom.size]
    }

    // Single Bedrooms
    const singleBedCount = parseInt(preferencesStore.spaces.singleBedroom.count)
    if (singleBedCount > 0) {
        area += singleBedCount * preferencesStore.areaConstants.singleBedroom[preferencesStore.spaces.singleBedroom.size]
    }

    // Bathrooms
    const bathroomCount = parseInt(preferencesStore.spaces.bathroom.count)
    area += bathroomCount * preferencesStore.areaConstants.bathroom[preferencesStore.spaces.bathroom.size]

    // WC
    const wcCount = parseInt(preferencesStore.spaces.wc.count)
    if (wcCount > 0) {
        area += wcCount * preferencesStore.areaConstants.wc
    }

    // Add 10% for circulation/walls
    return Math.round(area / 0.9)
})

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
    commonAreas: 1600,
    land: 3000
}

const totalCostPerSqm = computed(() => 
    COST_PER_SQM.construction + COST_PER_SQM.commonAreas + COST_PER_SQM.land
)

const totalCost = computed(() => 
    totalArea.value * totalCostPerSqm.value
)

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
            </CardDescription>
        </CardHeader>
        <CardContent class="space-y-3">
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span>Stan deweloperski</span>
                    <span class="font-medium">{{ formatPrice(COST_PER_SQM.construction) }} /m²</span>
                </div>
                <div class="flex justify-between">
                    <span>Części wspólne</span>
                    <span class="font-medium">{{ formatPrice(COST_PER_SQM.commonAreas) }} /m²</span>
                </div>
                <div class="flex justify-between">
                    <span>Zakup gruntu</span>
                    <span class="font-medium">{{ formatPrice(COST_PER_SQM.land) }} /m²</span>
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

