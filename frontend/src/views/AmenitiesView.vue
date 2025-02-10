<template>
    <div>
        <h1 class="text-3xl font-bold mb-6">Budynek</h1>
        <AmenitiesSelector />
        <CostCalculator />
    </div>
</template>

<script setup>
import CostCalculator from '@/components/preferences/CostCalculator.vue'
import AmenitiesSelector from '@/components/preferences/AmenitiesSelector.vue'
</script>