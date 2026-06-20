<script setup>
import { ref, onMounted } from 'vue'
import LoginView from '@/components/LoginView.vue'

const isLoggedIn = ref(false)

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('token')
})
</script>

<template>
  <!-- Main layout container with full screen min-height -->
  <div class="min-h-screen bg-gray-50 text-gray-900 antialiased font-sans flex flex-col">

    <!-- Case 1: NOT logged in (and not on doctor route) -> Show login perfectly centered, hide navbar -->
    <div v-if="!isLoggedIn && $route.path !== '/doctor'" class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-md">
        <LoginView />
      </div>
    </div>

    <!-- Case 2: Logged in (or on doctor route) -> Show standard wide application interface layout -->
    <template v-else>
      <!-- Topbar & Main Menu Router Links Navigation Layout -->
      <nav class="bg-white border-b border-gray-200 py-4 px-6 mb-8 shadow-xs">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <span class="text-xl font-black tracking-tight text-blue-600">🏥 Family Clinic Hub</span>

          <!-- Right side container housing login status and main tabs side by side -->
          <div class="flex flex-col sm:flex-row items-center gap-4">
            <!-- Force the login status box/logout button to sit neatly to the left of tabs -->
            <div v-if="isLoggedIn">
              <LoginView />
            </div>

            <!-- Navigation Tabs Link Hub -->
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
        </div>
      </nav>

      <!-- CONTENT DISPLAY LOGIC CONTEXT MATRIX -->
      <main class="max-w-7xl mx-auto px-6 pb-12 w-full flex-1">
        <div class="space-y-6">
          <!-- Crucial Vue-Router view canvas placeholder: Active route components render cleanly right here! -->
          <router-view />
        </div>
      </main>
    </template>

  </div>
</template>
