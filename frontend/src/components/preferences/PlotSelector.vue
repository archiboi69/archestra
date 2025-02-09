<template>
    <div>
        <h1>Plot Selector</h1>
        <div id="map" style="height:500px; width: 100%;"></div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { usePreferencesStore} from '@/stores/preferences'

const preferencesStore = usePreferencesStore()
const selectedPlotId = ref(null)

const pilotPlots = [
    { 
        id: 'plot-1',
        latitude: 52.398333, 
        longitude: 16.907000,
        area: 2500,
        maxUnits: 12,
        district: 'Łazarz',
        address: 'Ul. Gąsiorowskich 6',
        description: 'Działka z pozwoleniem na budowę'
    },
    { 
        id: 'plot-2',
        latitude: 52.413611, 
        longitude: 16.898333,
        area: 3000,
        maxUnits: 15,
        district: 'Jeżyce',
        address: 'Ul. Dąbrowskiego',
        description: 'Działka w spokojnej okolicy'
    },
    { 
        id: 'plot-3',
        latitude: 52.417222, 
        longitude: 16.900278,
        area: 2000,
        maxUnits: 10,
        district: 'Jeżyce',
        address: 'Ul. Janickiego',
        description: 'Działka blisko centrum'
    },
    { 
        id: 'plot-4',
        latitude: 52.416389, 
        longitude: 16.927222,
        area: 1800,
        maxUnits: 8,
        district: 'Stare Miasto',
        address: 'Al. Niepodległości',
        description: 'Działka z widokiem na park'
    },
    { 
        id: 'plot-5',
        latitude: 52.423611, 
        longitude: 16.910000,
        area: 2200,
        maxUnits: 11,
        district: 'Sołacz',
        address: 'Ul. Urbanowska',
        description: 'Działka w rozwijającej się dzielnicy'
    },
    { 
        id: 'plot-6',
        latitude: 52.361111, 
        longitude: 16.863889,
        area: 2700,
        maxUnits: 14,
        district: 'Kotowo',
        address: 'Ul. Mieleszyńska',
        description: 'Działka w historycznej części miasta'
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
                    <h3>${plot.district} - ${plot.address}</h3>
                    <p>${plot.description}</p>
                    <p>Powierzchnia: ${plot.area} m²</p>
                    <p>Max liczba mieszkań: ${plot.maxUnits}</p>
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

</style>