<script setup>
import { cn } from '@/lib/utils'
import { TabsContent } from 'radix-vue'
import { computed } from 'vue'

const props = defineProps({
  value: String,
  forceMount: Boolean,
  class: String,
})

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props
  return delegated
})
</script>

<template>
  <TabsContent
    :class="cn('mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', props.class)"
    v-bind="delegatedProps"
  >
    <slot />
  </TabsContent>
</template>
