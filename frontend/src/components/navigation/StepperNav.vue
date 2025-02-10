<script setup>
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'

// Define the steps
const steps = [
  { id: 'spaces', label: 'Mieszkanie', route: '/preferences' },
  { id: 'amenities', label: 'Budynek', route: '/amenities' },
  { id: 'location', label: 'Lokalizacja', route: '/location' },
  { id: 'summary', label: 'Podsumowanie', route: '/summary' }
]
</script>

<template>
  <div class="w-full border-b">
    <ScrollArea class="w-full">
      <Tabs default-value="spaces" class="w-full">
        <TabsList class="inline-flex w-full justify-start gap-6 p-4">
          <TabsTrigger
            v-for="step in steps"
            :key="step.id"
            :value="step.id"
            @click="$router.push(step.route)"
            class="flex items-center gap-2"
          >
            <span class="text-sm font-medium">{{ step.label }}</span>
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </ScrollArea>
  </div>
</template> 