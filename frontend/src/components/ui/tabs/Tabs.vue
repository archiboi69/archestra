<script setup>
import { TabsRoot, useForwardPropsEmits } from 'radix-vue'

const props = defineProps({
  defaultValue: String,
  value: String,
  onValueChange: Function,
  activationMode: String,
  orientation: String,
})

const emits = defineEmits(['update:value'])

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <TabsRoot v-bind="forwarded">
    <slot />
  </TabsRoot>
</template>
