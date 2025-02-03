<template>
    <div class="space-y-6">
        <!-- Common area finishes-->
        <Card>
            <CardHeader>
                <CardTitle>Wymagane części wspólne</CardTitle>
                <CardDescription>
                    W budynku wielorodzinnym części wspólne (klatka schodowa, korytarz, wózkarnia itp.) 
                    stanowią zazwyczaj 25% powierzchni całkowitej budynku.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <RadioGroup
                    v-model="preferencesStore.amenities.commonAreaFinish"
                    class="space-y-2"
                >
                    <div v-for="(finish, key) in commonAreaFinishes" :key="key"
                        class="flex items-center space-x-2"
                    >
                        <RadioGroupItem :id="`common-area-${key}`" :value="key" />
                        <label 
                            :for="`common-area-${key}`"
                            class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            {{ finish.label }} ({{ (finish.price * preferencesStore.commonAreaShare).toLocaleString() }} zł)
                        </label>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>

        <!-- Elevator -->
        <Card>
            <CardHeader>
                <CardTitle>Winda</CardTitle>
                <CardDescription>
                    Winda może być obowiązkowa w wyższych budynkach. Koszt windy rozkłada się w zależności od liczby mieszkań.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch 
                        id="elevator" 
                        :checked="preferencesStore.amenities.elevator"
                        @update:modelValue="() => preferencesStore.toggleAmenity('elevator')"
                    />
                    <Label for="elevator">
                        + {{ preferencesStore.pricesConstants.elevator.toLocaleString() }} zł
                    </Label>
                </div>
            </CardContent>
        </Card>

        <!-- Laundry -->
        <Card>
            <CardHeader>
                <CardTitle>Pralnia</CardTitle>
                <CardDescription>
                    Wspólna pralnia z pralkami i suszarkami dostępna dla mieszkańców.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch id="laundry" v-model="preferencesStore.amenities.laundry" />
                    <Label for="laundry">+ {{ preferencesStore.pricesConstants.laundry.toLocaleString() }} zł</Label>
                </div>
            </CardContent>
        </Card>

        <!-- Workshop -->
        <Card>
            <CardHeader>
                <CardTitle>Warsztat</CardTitle>
                <CardDescription>
                    Pomieszczenie warsztatowe z podstawowymi narzędziami dla majsterkowiczów.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch id="workshop" v-model="preferencesStore.amenities.workshop" />
                    <Label for="workshop">+ {{ preferencesStore.pricesConstants.workshop.toLocaleString() }} zł</Label>
                </div>
            </CardContent>
        </Card>

        <!-- Lounge -->
        <Card>
            <CardHeader>
                <CardTitle>Sala klubowa</CardTitle>
                <CardDescription>
                    Wspólna przestrzeń do rekreacji, pracy i organizacji spotkań.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch id="lounge" v-model="preferencesStore.amenities.lounge" />
                    <Label for="lounge">+ {{ preferencesStore.pricesConstants.lounge.toLocaleString() }} zł</Label>
                </div>
            </CardContent>
        </Card>

        <!-- Fitness -->
        <Card>
            <CardHeader>
                <CardTitle>Siłownia</CardTitle>
                <CardDescription>
                    Sala fitness z podstawowym sprzętem do ćwiczeń.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch id="fitness" v-model="preferencesStore.amenities.fitness" />
                    <Label for="fitness">+ {{ preferencesStore.pricesConstants.fitness.toLocaleString() }} zł</Label>
                </div>
            </CardContent>
        </Card>

        <!-- Sauna -->
        <Card>
            <CardHeader>
                <CardTitle>Sauna</CardTitle>
                <CardDescription>
                    Sauna fińska z szatnią i prysznicami.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="flex items-center space-x-2">
                    <Switch id="sauna" v-model="preferencesStore.amenities.sauna" />
                    <Label for="sauna">+ {{ preferencesStore.pricesConstants.sauna.toLocaleString() }} zł</Label>
                </div>
            </CardContent>
        </Card>
    </div>
</template>

<script setup>
// Imports
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { usePreferencesStore } from '@/stores/preferences'

// Store initialization
const preferencesStore = usePreferencesStore()

const commonAreaFinishes = {
    economy: {
        label: 'Ekonomiczny',
        price: preferencesStore.pricesConstants.commonAreaFinish.economy
    },
    standard: {
        label: 'Standardowy',
        price: preferencesStore.pricesConstants.commonAreaFinish.standard
    },
    premium: {
        label: 'Premium',
        price: preferencesStore.pricesConstants.commonAreaFinish.premium
    }
}

</script>