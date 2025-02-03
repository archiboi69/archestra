<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  class: String,
})
</script>

<template>
  <div :class="cn('rounded-lg border bg-(--color-card) text-(--color-card-foreground) shadow-sm', props.class)">
    <slot />
  </div>
</template>
