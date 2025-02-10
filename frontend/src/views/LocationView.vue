<template>
    <div>
        <h1 class="text-3xl font-bold mb-6">Lokalizacja</h1>
        <PlotSelector />
        <CostCalculator />
    </div>
</template>

<script setup>
import CostCalculator from '@/components/preferences/CostCalculator.vue'
import { usePreferencesStore } from '@/stores/preferences'
import PlotSelector from '@/components/preferences/PlotSelector.vue'

const preferencesStore = usePreferencesStore()

</script>