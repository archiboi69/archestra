import { cva } from 'class-variance-authority'

export const toggleVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-(--color-background) transition-colors hover:bg-(--color-muted) hover:text-(--color-muted-foreground) focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-(--color-ring) focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=on]:bg-(--color-accent) data-[state=on]:text-(--color-accent-foreground)',
  {
    variants: {
      variant: {
        default: 'bg-transparent',
        outline: 'border border-(--color-input) bg-(--color-background) hover:bg-(--color-accent) hover:text-(--color-accent-foreground)',
      },
      size: {
        default: 'h-10 px-3',
        sm: 'h-9 px-2.5',
        lg: 'h-11 px-5',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export { default as Toggle } from './Toggle.vue' 