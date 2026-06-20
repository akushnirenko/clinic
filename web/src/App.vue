<script setup>
import { ref, onMounted } from 'vue'
import LoginView from '@/components/LoginView.vue'

const isLoggedIn = ref(false)

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('token')
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 antialiased font-sans pb-12">

    <!-- Topbar & Main Menu Router Links Navigation Layout -->
    <nav class="bg-white border-b border-gray-200 py-4 px-6 mb-8 shadow-xs">
      <!-- Changed from max-w-5xl to max-w-7xl for a wider desktop presence -->
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
        <span class="text-xl font-black tracking-tight text-blue-600">🏥 Детская поликлиника</span>

        <!-- Navigation Tabs Link Hub (Only fully active if logged in) -->
        <div class="flex items-center space-x-1 bg-gray-100 p-1 rounded-xl text-sm font-medium">
          <router-link
            to="/"
            class="px-4 py-2 rounded-lg transition"
            active-class="bg-white text-blue-600 shadow-xs font-semibold"
          >
            👨‍👩‍👧‍👦 Моя Семья
          </router-link>

          <router-link
            to="/book"
            class="px-4 py-2 rounded-lg transition"
            active-class="bg-white text-blue-600 shadow-xs font-semibold"
          >
            📅 Запись к Врачу
          </router-link>

          <router-link
            to="/doctor"
            class="px-4 py-2 rounded-lg transition"
            active-class="bg-white text-blue-600 shadow-xs font-semibold"
          >
            🩺 Панель Врача
          </router-link>
        </div>
      </div>
    </nav>

    <!-- CONTENT DISPLAY LOGIC CONTEXT MATRIX -->
    <!-- Wrapped content areas in a responsive grid container matching the nav width -->
    <main class="max-w-7xl mx-auto px-6">
      <div v-if="!isLoggedIn && $route.path !== '/doctor'">
        <!-- If visitor wants to see parent pages without a token, show standard login prompt -->
        <LoginView />
      </div>

      <div v-else class="space-y-6">
        <!-- LoginView header line contains the small floating 'Sign Out' action button panel -->
        <LoginView v-if="isLoggedIn" />

        <!-- Crucial Vue-Router view canvas placeholder: Active route components render cleanly right here! -->
        <router-view />
      </div>
    </main>

  </div>
</template>
