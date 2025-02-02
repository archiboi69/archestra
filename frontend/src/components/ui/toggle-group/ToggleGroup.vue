<script setup>
import { cn } from '@/lib/utils'
import { ToggleGroupRoot, useForwardPropsEmits } from 'radix-vue'
import { computed, provide } from 'vue'

const props = defineProps({
  class: String,
  variant: String,
  size: String,
  type: String,
  defaultValue: [String, Array],
  value: [String, Array],
})

const emits = defineEmits(['update:value'])

provide('toggleGroup', {
  variant: props.variant,
  size: props.size,
})

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props
  return delegated
})

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <ToggleGroupRoot v-bind="forwarded" :class="cn('flex items-center justify-center gap-1', props.class)">
    <slot />
  </ToggleGroupRoot>
</template>
