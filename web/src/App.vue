<script setup>
import { ref, onMounted } from 'vue'
import LoginView from './components/LoginView.vue'
import Dashboard from './components/Dashboard.vue'

const isLoggedIn = ref(false)

onMounted(() => {
  // Check browser state memory space to verify authentication status
  isLoggedIn.value = !!localStorage.getItem('token')
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 antialiased font-sans pb-12">
    <!-- Main App Navigation Topbar -->
    <nav class="bg-white border-b border-gray-200 py-4 px-6 mb-8 shadow-xs">
      <div class="max-w-5xl mx-auto flex justify-between items-center">
        <span class="text-xl font-black tracking-tight text-blue-600">🏥 Family Clinic Hub</span>
        <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 uppercase tracking-wider">v1.0 Dev</span>
      </div>
    </nav>

    <!-- If the user is a visitor, render the login box container -->
    <div v-if="!isLoggedIn">
      <LoginView />
    </div>

    <!-- If the user has securely logged in, render the operational management dashboard panel -->
    <div v-else>
      <LoginView /> <!-- Kept here to render the clean tiny top 'Sign Out' toolbar button panel -->
      <Dashboard />
    </div>
  </div>
</template>
