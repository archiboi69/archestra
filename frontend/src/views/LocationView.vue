<template>
    <div>
        <h1 class="text-3xl font-bold mb-6">Lokalizacja</h1>
        <DistrictSelector />
        <CostCalculator />
    </div>
</template>

<script setup>
import DistrictSelector from '@/components/location/DistrictSelector.vue'
import CostCalculator from '@/components/preferences/CostCalculator.vue'
import { usePreferencesStore } from '@/stores/preferences'

const preferencesStore = usePreferencesStore()

</script>