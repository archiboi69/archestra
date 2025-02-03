<script setup>
import { cn } from '@/lib/utils'
import { Label as RadixLabel } from 'radix-vue'
import { computed } from 'vue'

const props = defineProps({
    for: String,
    asChild: Boolean,
    class: String
})

const delegatedProps = computed(() => {
    const { class: _, ...delegated } = props
    return delegated
})
</script>

<template>
    <RadixLabel
        v-bind="delegatedProps"
        :class="cn(
            'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
            props.class
        )"
    >
        <slot />
    </RadixLabel>
</template>
