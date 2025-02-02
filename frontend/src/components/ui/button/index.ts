import type { VariantProps } from 'class-variance-authority'
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

export type ButtonVariants = VariantProps<typeof buttonVariants>
export { default as Button } from './Button.vue' 