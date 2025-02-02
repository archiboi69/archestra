<script setup>
import Button from '@/components/ui/button/Button.vue'
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen">
    <header class="text-center mb-8">
      <h1 class="text-4xl font-bold text-(--color-foreground)">Archestra</h1>
      <p class="text-lg text-(--color-muted-foreground)">Skonfiguruj swoje mieszkanie</p>
    </header>

    <main>
      <Button
        as="RouterLink"
        to="/preferences"
        size="lg"
        variant="default"
        class="font-semibold">
        Zacznij
      </Button>
    </main>
  </div>
</template>