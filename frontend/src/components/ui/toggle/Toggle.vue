<script setup>
import { cn } from '@/lib/utils'
import { Toggle, useForwardPropsEmits } from 'radix-vue'
import { computed } from 'vue'
import { toggleVariants } from '.'

const props = defineProps({
  class: String,
  variant: {
    type: String,
    default: 'default'
  },
  size: {
    type: String,
    default: 'default'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  pressed: Boolean,
  defaultPressed: Boolean,
})

const emits = defineEmits(['update:pressed'])

const delegatedProps = computed(() => {
  const { class: _, size, variant, ...delegated } = props
  return delegated
})

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <Toggle
    v-bind="forwarded"
    :class="cn(toggleVariants({ variant, size }), props.class)"
  >
    <slot />
  </Toggle>
</template>
