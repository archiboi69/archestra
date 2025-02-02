<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { Primitive, type PrimitiveProps } from 'radix-vue'
import { type ButtonVariants, buttonVariants } from '.'
import type { RouteLocationRaw } from 'vue-router'
import { RouterLink } from 'vue-router'

interface Props extends /* @vue-ignore */ PrimitiveProps {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  class?: HTMLAttributes['class']
  to?: RouteLocationRaw
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
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