import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/components/Dashboard.vue'
import Booking from '@/components/Booking.vue'
import DoctorPanel from '@/components/DoctorPanel.vue' // Placeholder for now

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/book',
    name: 'Booking',
    component: Booking,
    meta: { requiresAuth: true }
  },
  {
    path: '/doctor',
    name: 'DoctorPanel',
    component: DoctorPanel
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Optional Navigation Guard: Redirects to login if token is missing
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    // If not logged in and page requires auth, stay on root (where Login prompt is shown)
    next()
  } else {
    next()
  }
})

export default router
