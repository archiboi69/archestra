<template>
    <div>
        <div id="map" style="height:500px; width: 100%;"></div>
    </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { usePreferencesStore} from '@/stores/preferences'

const preferencesStore = usePreferencesStore()
const selectedPlotId = ref(null)

const chosenFlatArea = computed(() => preferencesStore.totalArea)

const calculateLandCost = (costPerSqm) => {
    return costPerSqm * chosenFlatArea.value
}

const formatCurrency = (value) => {
    return value.toLocaleString('pl-PL', {
        style: 'currency',
        currency: 'PLN',
        maximumFractionDigits: 0
    })
}
const pilotPlots = [
    { 
        id: 'plot-1',
        latitude: 52.398333, 
        longitude: 16.907000,
        totalArea: 2500,
        obreb: 'Łazarz',
        address_point: 'Gąsiorowskich 6',
        maxStories: 7,
        density_per_500m2: 50, // flats per 500m2 of plot area
        land_cost_per_m2: 3000, // land cost per 1m2 of usable flat area (PUM)
    },
    { 
        id: 'plot-2',
        latitude: 52.413611, 
        longitude: 16.898333,
        totalArea: 3000,
        obreb: 'Jeżyce',
        address_point: 'Dąbrowskiego 80',
        maxStories: 15,
        density_per_500m2: 30, // flats per 500m2 of plot area
        land_cost_per_m2: 3500, // land cost per 1m2 of usable flat area (PUM)
    },
    { 
        id: 'plot-3',
        latitude: 52.417222, 
        longitude: 16.900278,
        totalArea: 2000,
        obreb: 'Jeżyce',
        address_point: 'Janickiego',
        maxStories: 10,
        density_per_500m2: 25, // flats per 500m2 of plot area
        land_cost_per_m2: 3200, // land cost per 1m2 of usable flat area (PUM)
    },
    { 
        id: 'plot-4',
        latitude: 52.416389, 
        longitude: 16.927222,
        totalArea: 1800,
        obreb: 'Stare Miasto',
        address_point: 'Niepodległości',
        maxStories: 8,
        density_per_500m2: 20, // flats per 500m2 of plot area
        land_cost_per_m2: 3300, // land cost per 1m2 of usable flat area (PUM)
    },
    { 
        id: 'plot-5',
        latitude: 52.423611, 
        longitude: 16.910000,
        totalArea: 2200,
        obreb: 'Sołacz',
        address_point: 'Urbanowska',
        maxStories: 11,
        density_per_500m2: 22, // flats per 500m2 of plot area
        land_cost_per_m2: 3400, // land cost per 1m2 of usable flat area (PUM)
    },
    { 
        id: 'plot-6',
        latitude: 52.361111, 
        longitude: 16.863889,
        totalArea: 2700,
        obreb: 'Kotowo',
        address_point: 'Mieleszyńska',
        maxStories: 14,
        density_per_500m2: 28, // flats per 500m2 of plot area
        land_cost_per_m2: 3600, // land cost per 1m2 of usable flat area (PUM)
    }
]

onMounted(() => {
    // Initialize the map centered on Poznań
    const map = L.map('map').setView([52.4064, 16.9252], 12)

    // Add OSM tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    // Add markers for each plot
    pilotPlots.forEach(plot => {
        L.marker([plot.latitude, plot.longitude])
            .addTo(map)
            .bindPopup(`
                <div class="plot-popup">
                    <h3>${plot.obreb} - ${plot.address_point}</h3>
                    <p>Powierzchnia: ${plot.totalArea} m²</p>
                    <p>maks. ${plot.maxStories} kondygnacji nadziemnych</p>
                    <p>${plot.density_per_500m2} mieszkań/500 m² działki</p>
                    <p>Koszt udziału w gruncie: ${formatCurrency(calculateLandCost(plot.land_cost_per_m2))}</p>
                    <button 
                        class="select-plot-btn" 
                        data-plot-id="${plot.id}"
                    >
                        Wybierz działkę
                    </button>
                </div>
            `)
            .on('popupopen', (e) => {
                // Add click handler after popup opens
                const btn = document.querySelector(`button[data-plot-id="${plot.id}"]`)
                if (btn) {
                    btn.addEventListener('click', () => selectPlot(plot))
                }
            })
    })
})

const selectPlot = (plot) => {
    try {
        selectedPlotId.value = plot.id
        preferencesStore.selectPlot(plot)
    } catch (error) {
        console.error('Error selecting plot:', error)
    }
}
</script>

<style>
/* Leaflet popup customization */
.leaflet-popup-content-wrapper {
    padding: 0;
    border-radius: 8px;
    background-color: var(--color-card);
    color: var(--color-card-foreground);
}

.leaflet-popup-content {
    margin: 0;
    min-width: 200px;
}

.leaflet-popup-tip {
    background-color: var(--color-card);
}

/* Our popup content styles */
.plot-popup {
    padding: 1rem;
}

.plot-popup h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}

.plot-popup p {
    font-size: 0.875rem;
    margin: 0.25rem 0;
    color: var(--color-muted-foreground);
}

.select-plot-btn {
    width: 100%;
    margin-top: 1rem;
    padding: 0.5rem;
    background-color: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.2s;
}

.select-plot-btn:hover {
    opacity: 0.9;
}
</style>