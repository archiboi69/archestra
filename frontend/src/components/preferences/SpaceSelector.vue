<template>
    <form>
        <div class="flex flex-col gap-2">
            <label for="double-bedrooms">Double bedrooms</label>
            <select id="double-bedrooms" v-model="preferencesStore.spaces.doubleBedrooms" @change="logChange">
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
        </div>
        <div class="flex flex-col gap-2">
            <label for="single-bedrooms">Single bedrooms</label>
            <select id="single-bedrooms" v-model="preferencesStore.spaces.singleBedrooms" @change="logChange">
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
            <button type="button" @click="preferencesStore.spaces.singleBedrooms++">+ Add bedroom</button>
        </div>
        <div class="flex flex-col gap-2">
            <label for="bathrooms">Bathrooms</label>
            <select id="bathrooms" v-model="preferencesStore.spaces.bathrooms" @change="logChange">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
            </select>
        </div>
        <div class="flex flex-col gap-2">
            <label for="wc">WC</label>
            <select id="wc" v-model="preferencesStore.spaces.wc" @change="logChange">
                <option value="0">0</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
            </select>
        </div>
        <div class="flex flex-col gap-2">
            <label for="kitchen">Kitchen or kitchenette</label>
            <select id="kitchen" v-model="preferencesStore.spaces.kitchen" @change="logChange">
                <option value="kitchen">Kitchen</option>
                <option value="kitchenette">Kitchenette</option>
            </select>
        </div>
    </form>

</template>

<script setup>
import { usePreferencesStore } from '@/stores/preferences';

const preferencesStore = usePreferencesStore();

// a function that logs the changes to console
const logChange = () => {
    console.log(preferencesStore.spaces);
};
</script>

<style>
</style>