<script setup>
import { ref } from 'vue'
import api from '@/api.js'

// Form inputs
const email = ref('')
const password = ref('')

// Reactive component states
const errorMessage = ref('')
const isLoading = ref(false)
const isAuthenticated = ref(!!localStorage.getItem('token'))

const handleLogin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    // FastAPI's OAuth2PasswordRequestForm requires a URL-encoded payload
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    // Store the secure cryptographed authentication token
    localStorage.setItem('token', response.data.access_token)
    isAuthenticated.value = true

    // Quick trick to let the Dashboard component know it's time to fetch data
    window.location.reload()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Invalid email or password.'
  } finally {
    isLoading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  isAuthenticated.value = false
  window.location.reload()
}
</script>

<template>
  <div class="max-w-md mx-auto my-12 p-6 bg-white rounded-xl border border-gray-200 shadow-xs">

    <!-- LOGIN FORM LAYER -->
    <div v-if="!isAuthenticated">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Family Clinic Login</h2>
        <p class="text-sm text-gray-400 mt-1">Sign in to access your parent dashboard</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email Address</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="parent@example.com"
            class="mt-1 w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm transition"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="mt-1 w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm transition"
          />
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition disabled:bg-blue-400 disabled:cursor-not-allowed text-sm shadow-xs"
        >
          {{ isLoading ? 'Authenticating...' : 'Sign In' }}
        </button>
      </form>

      <!-- Context Error Alert -->
      <p v-if="errorMessage" class="text-sm text-red-600 mt-4 bg-red-50 p-2.5 rounded-lg border border-red-100 text-center">
        {{ errorMessage }}
      </p>
    </div>

    <!-- LOGGED IN HEADER STATUS -->
    <div v-else class="flex justify-between items-center bg-gray-50 p-3 rounded-lg border border-gray-100">
      <div class="flex items-center space-x-2">
        <span class="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></span>
        <p class="text-sm font-medium text-gray-600">Authenticated Session Active</p>
      </div>
      <button
        @click="handleLogout"
        class="text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium px-3 py-1.5 rounded-md transition"
      >
        Sign Out
      </button>
    </div>

  </div>
</template>
