<script setup>
import { usePreferencesStore } from '@/stores/preferences'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { computed } from 'vue'

const preferencesStore = usePreferencesStore()

// Helper function to format currency
const formatCurrency = (value) => {
    return value.toLocaleString('pl-PL', { 
        style: 'currency', 
        currency: 'PLN',
        maximumFractionDigits: 0
    })
}

// Calculate total land cost for each district
const getDistrictCost = (landPrice) => {
    return landPrice * preferencesStore.totalArea
}
</script>

<template>
    <div class="space-y-6">
        <Card v-for="district in preferencesStore.availableDistricts" :key="district.properties.id">
            <CardHeader>
                <CardTitle>{{ district.properties.name }}</CardTitle>
                <CardDescription>
                    {{ district.properties.description }}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <Switch 
                            :id="district.properties.id"
                            :checked="preferencesStore.location.selectedDistricts.includes(district.properties.id)"
                            @update:modelValue="() => preferencesStore.toggleDistrict(district.properties.id)"
                        />
                        <Label :for="district.properties.id">
                            Koszt gruntu
                        </Label>
                    </div>
                    <div class="text-sm font-medium">
                        {{ formatCurrency(getDistrictCost(district.properties.landPrice)) }}
                    </div>
                </div>
            </CardContent>
        </Card>
    </div>
</template> 