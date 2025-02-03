<script setup>
import { usePreferencesStore } from '@/stores/preferences'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'

const preferencesStore = usePreferencesStore()
</script>

<template>
    <div class="space-y-6">
        <Card v-for="district in preferencesStore.availableDistricts" :key="district.properties.id">
            <CardHeader>
                <CardTitle>{{ district.properties.name }}</CardTitle>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch 
                        :id="district.properties.id"
                        :checked="preferencesStore.location.selectedDistricts.includes(district.properties.id)"
                        @update:modelValue="() => preferencesStore.toggleDistrict(district.properties.id)"
                    />
                    <Label :for="district.properties.id">
                        {{ district.properties.landPrice }} zł/m²
                    </Label>
                </div>
            </CardContent>
        </Card>
    </div>
</template> 