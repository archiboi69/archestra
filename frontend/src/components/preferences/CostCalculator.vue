<script setup>
import { usePreferencesStore } from '@/stores/preferences';

const preferencesStore = usePreferencesStore();

</script>

<template>
    <div>
        <h1>Cost Calculator</h1>
        <p>Total area: {{ preferencesStore.totalArea }} m2</p>
        <p>Construction cost (without land): {{ (preferencesStore.totalArea * 5100).toLocaleString('pl-PL', { style: 'currency', currency: 'PLN' }) }}</p>
    </div>
</template>

