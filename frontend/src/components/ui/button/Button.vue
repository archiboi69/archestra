<script setup>
import { cn } from '@/lib/utils'
import { Primitive } from 'radix-vue'
import { buttonVariants } from './index.js'
import { RouterLink } from 'vue-router'

const props = defineProps({
  class: String,
  variant: String,
  size: String,
  as: {
    type: String,
    default: 'button'
  },
  to: [String, Object],
  asChild: Boolean
})
</script>

<template>
  <RouterLink
    v-if="to"
    :to="to"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </RouterLink>

  <Primitive
    v-else
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </Primitive>
</template> 