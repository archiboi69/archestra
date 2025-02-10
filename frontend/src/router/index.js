import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import PreferencesView from '@/views/PreferencesView.vue'
import AmenitiesView from '@/views/AmenitiesView.vue'
import LocationView from '@/views/LocationView.vue'
import SummaryView from '@/views/SummaryView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/preferences',
      name: 'preferences',
      component: PreferencesView,
    },
    {
      path: '/amenities',
      name: 'amenities',
      component: AmenitiesView,
    },
    {
      path: '/location',
      name: 'location',
      component: LocationView,
    },
    {
      path: '/summary',
      name: 'summary',
      component: SummaryView,
    },
  ],
})

export default router
