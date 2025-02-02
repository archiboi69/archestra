# Using Tailwind CSS v4 with shadcn-vue Components and Radix Vue and JavaScript and Vue 3

## Setup

1. **Import Tailwind**
```css
/* Don't use @tailwind directives anymore */
@import "tailwindcss";
```

2. **Global CSS Setup**
```css
@theme {
  /* Theme configuration */
  --radius: 0.5rem;
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);

  /* Base colors */
  --color-border: currentColor; /* Default border color is now currentColor */
  --color-input: hsl(216 34% 17%);
  --color-ring: hsl(216 34% 17%);
  --color-background: hsl(224 71% 4%);
  --color-foreground: hsl(213 31% 91%);
  
  /* Component-specific colors */
  --color-primary: hsl(210 40% 98%);
  --color-primary-foreground: hsl(222.2 47.4% 1.2%);
  --color-secondary: hsl(222.2 47.4% 11.2%);
  --color-secondary-foreground: hsl(210 40% 98%);
  --color-destructive: hsl(0 63% 31%);
  --color-destructive-foreground: hsl(210 40% 98%);
  --color-muted: hsl(223 47% 11%);
  --color-muted-foreground: hsl(215.4 16.3% 56.9%);
  --color-accent: hsl(216 34% 17%);
  --color-accent-foreground: hsl(210 40% 98%);
}

/* Base styles */
@layer base {
  html, body {
    background-color: var(--color-background);
    color: var(--color-foreground);
    min-height: 100vh;
  }
}
```

3. **Utils Setup**
```javascript
// utils.js - Simple class merging utility
export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}
```

## Component Pattern

1. **Define Component-Specific Utilities**
```css
/* Place after @theme block */
@utility button-base {
  display: inline-flex;
  align-items: center;
  justify-center;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
```

2. **Component Structure (JavaScript Version)**
```vue
<!-- Button.vue -->
<script setup>
import { cn } from '@/lib/utils'
import { Primitive } from 'radix-vue'
import { buttonVariants } from '.'

const props = defineProps({
  variant: String,
  size: String,
  class: String,
  as: {
    type: String,
    default: 'button'
  },
  // Add routing props if needed
  to: [String, Object]
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
```

3. **Component Variants**
```javascript
// index.js
import { cva } from 'class-variance-authority'

export const buttonVariants = cva('button-base', {
  variants: {
    variant: {
      default: 'bg-(--color-primary) text-(--color-primary-foreground) hover:bg-primary/90',
      destructive: 'bg-(--color-destructive) text-(--color-destructive-foreground) hover:bg-destructive/90',
      outline: 'border border-(--color-input) bg-(--color-background) hover:bg-(--color-accent) hover:text-(--color-accent-foreground)',
      secondary: 'bg-(--color-secondary) text-(--color-secondary-foreground) hover:bg-secondary/80',
      ghost: 'hover:bg-(--color-accent) hover:text-(--color-accent-foreground)',
      link: 'text-(--color-primary) underline-offset-4 hover:underline',
    },
    size: {
      default: 'h-10 px-4 py-2',
      sm: 'h-9 px-3',
      lg: 'h-11 px-8',
      icon: 'h-10 w-10',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'default',
  },
})
```

## Complex Components (e.g., Tabs)

When working with complex Radix components, convert TypeScript interfaces to JavaScript props:

```vue
<!-- Tabs.vue -->
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
```

## Best Practices

1. Use CSS variables directly when possible
2. Specify border colors explicitly
3. Use `@utility` for component base styles
4. Use parentheses syntax for CSS variables
5. Consider hover as progressive enhancement
6. Use semantic color names
7. Keep component-specific utilities in `global.css`
8. Convert TypeScript interfaces to JavaScript props when not using TypeScript
9. Use computed properties for prop delegation in complex components
10. Handle routing cases explicitly in components that can be links

## Common Issues & Solutions

1. **TypeScript Requirements**
   - Either install TypeScript as dev dependency
   - Or convert components to JavaScript using proper prop definitions

2. **Radix Vue Integration**
   - Use `useForwardPropsEmits` for event handling
   - Use `useForwardProps` for prop forwarding
   - Handle component composition with `asChild` pattern

3. **Router Integration**
   - Handle routing props explicitly
   - Use conditional rendering for RouterLink vs regular components

## Usage Example

```vue
<template>
  <Button
    as="RouterLink"
    to="/preferences"
    size="lg"
    variant="default"
    class="font-semibold">
    Start
  </Button>
</template>

<script setup>
import Button from '@/components/ui/button/Button.vue'
</script>
```

## Best Practices

1. Use CSS variables directly when possible instead of utilities
2. Specify border colors explicitly (no more default gray-200)
3. Use `@utility` for component base styles
4. Use parentheses syntax for CSS variables
5. Consider hover as progressive enhancement
6. Use semantic color names in your theme variables
7. Keep component-specific utilities in `global.css`
