<script setup>
import { toggleVariants } from '@/components/ui/toggle'
import { cn } from '@/lib/utils'
import { ToggleGroupItem, useForwardProps } from 'radix-vue'
import { computed, inject } from 'vue'

const props = defineProps({
  class: String,
  variant: String,
  size: String,
  value: [String, Number],
  disabled: Boolean,
  asChild: Boolean,
})

const context = inject('toggleGroup', {})

const delegatedProps = computed(() => {
  const { class: _, variant, size, ...delegated } = props
  return delegated
})

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <ToggleGroupItem
    v-bind="forwardedProps" 
    :class="cn(toggleVariants({
      variant: context.variant || variant,
      size: context.size || size,
    }), props.class)"
  >
    <slot />
  </ToggleGroupItem>
</template>
