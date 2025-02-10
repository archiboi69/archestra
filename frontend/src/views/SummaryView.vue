<template>
    <div class="container mx-auto py-6">
        <h1>Podsumowanie</h1>
        <Card>
            <CardHeader>
                <CardTitle> {{ apartmentType }} </CardTitle>
                <CardDescription> Powierzchnia użytkowa {{ totalArea }} m² 
                    <div>
                        {{ obreb }} - {{ addressPoint }}
                    </div>
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex-col">
                    <div class="flex justify-between">
                        <span>Stan deweloperski</span>
                        <span>{{ formatCurrency(constructionCost) }}</span>
                    </div>
                    <div class="bg-muted-foreground/20 rounded-md p-2"></div>
                </div>
            </CardContent>
        </Card>
    </div>
</template>

<script setup>
import { Card, CardHeader, CardTitle, CardDescription, CardContent} from '@/components/ui/card/index'
import { usePreferencesStore } from '@/stores/preferences'
import { computed } from 'vue'

const preferencesStore = usePreferencesStore()
const selectedPlot = computed(() => preferencesStore.location.selectedPlot)

const obreb = 'Łazarz'
const addressPoint = 'Gąsiorowskich 6'
const totalArea = 51
const apartmentType = 'Mieszkanie dwupokojowe'
const constructionCost = 1000000
const landCost = 200000
const amenitiesCost = 100000

const formatCurrency = (value) => {
    return value.toLocaleString('pl-PL', {
        style: 'currency',
        currency: 'PLN',
        maximumFractionDigits: 0
    })
}


</script>

