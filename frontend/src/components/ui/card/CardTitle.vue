<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = defineProps({
  class: String,
  as: {
    type: String,
    default: 'h3',
  },
})
</script>

<template>
  <component
    :is="as"
    :class="cn('text-2xl font-semibold leading-none tracking-tight', props.class)"
  >
    <slot />
  </component>
</template>
