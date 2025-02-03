<template>
    <div class="container mx-auto py-6">
        <h1 class="text-3xl font-bold mb-6">Konfigurator mieszkania</h1>
        <SpaceSelector />
        <CostCalculator />
    </div>
</template>

<script setup>
import SpaceSelector from '@/components/preferences/SpaceSelector.vue'
import CostCalculator from '@/components/preferences/CostCalculator.vue'

console.log('PreferencesView mounted')
</script>