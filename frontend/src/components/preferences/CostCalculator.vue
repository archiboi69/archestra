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

const constructionCostPerSqm = computed(() => COST_PER_SQM.construction)

// Calculate absolute costs
const constructionCost = computed(() => 
    totalArea.value * constructionCostPerSqm.value
)

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

const landCostPerSqm = computed(() => preferencesStore.landCostPerSqm)

const landCost = computed(() => totalArea.value * landCostPerSqm.value)

const totalCost = computed(() => 
    constructionCost.value + 
    amenitiesCost.value + 
    landCost.value
)

const totalCostPerSqm = computed(() => 
    Math.round(totalCost.value / totalArea.value)
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

const selectedPlot = computed(() => preferencesStore.location.selectedPlot)
</script>

<template>
    <Card class="fixed bottom-4 right-4 w-96 shadow-lg bg-background/95 backdrop-blur z-[1000]">
        <CardHeader>
            <CardTitle>{{ apartmentType }}</CardTitle>
            <CardDescription>
                Powierzchnia użytkowa {{ totalArea }} m²
                <div v-if="selectedPlot" class="mt-1">
                    {{ selectedPlot.obreb }} - {{ selectedPlot.address_point }}
                </div>
            </CardDescription>
        </CardHeader>
        <CardContent class="space-y-3">
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span>Stan deweloperski</span>
                    <span class="font-medium">{{ formatCurrency(constructionCost) }}</span>
                </div>
                <div class="flex justify-between">
                    <span>Udział w części wspólnej</span>
                    <span class="font-medium">{{ formatCurrency(amenitiesCost) }}</span>
                </div>
                <div class="flex justify-between">
                    <span>Udział w gruncie</span>
                    <span class="font-medium">{{ formatCurrency(landCost) }}</span>
                </div>
                <div class="flex justify-between pt-2 border-t text-base font-medium">
                    <span>Całkowity koszt mieszkania</span>
                    <span>{{ formatCurrency(totalCost) }}</span>
                </div>
            </div>
            <div class="flex justify-between pt-2 border-t text-sm text-muted-foreground">
                <span>Koszt m² mieszkania</span>
                <span>{{ formatPrice(totalCostPerSqm) }} /m²</span>
            </div>
        </CardContent>
    </Card>
</template>

