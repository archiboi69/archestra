<script setup>
import { RouterView, useRoute } from 'vue-router'
import StepperNav from '@/components/navigation/StepperNav.vue'
import { computed } from 'vue'

const route = useRoute()
const isHome = computed(() => route.path === '/')
</script>

<template>
  <!-- Home page without navigation -->
  <div v-if="isHome" class="min-h-screen bg-(--color-background)">
    <RouterView />
  </div>

  <!-- Other pages with navigation -->
  <div v-else class="min-h-screen bg-(--color-background)">
    <StepperNav />
    <main class="container mx-auto p-6">
      <RouterView />
    </main>
  </div>
</template>