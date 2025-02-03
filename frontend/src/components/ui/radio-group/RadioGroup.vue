<script setup>
import { cn } from '@/lib/utils'
import { RadioGroupRoot, useForwardPropsEmits } from 'radix-vue'
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  defaultValue: String,
  disabled: Boolean,
  required: Boolean,
  name: String,
  class: String,
})

const emits = defineEmits(['update:modelValue'])

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props
  return delegated
})

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <RadioGroupRoot
    :class="cn('grid gap-2', props.class)"
    v-bind="forwarded"
  >
    <slot />
  </RadioGroupRoot>
</template>
