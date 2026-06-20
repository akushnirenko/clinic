<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'

const children = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

// Form State for adding a new child
const showModal = ref(false)
const firstName = ref('')
const lastName = ref('')
const birthDate = ref('')
const snils = ref('')

// Fetch children records linked to the logged-in parent
const fetchChildren = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    const response = await api.get('/patients/')
    children.value = response.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Failed to load children profiles.'
  } finally {
    isLoading.value = false
  }
}

// Submit new child profile payload
const handleAddChild = async () => {
  try {
    errorMessage.value = ''
    const payload = {
      first_name: firstName.value,
      last_name: lastName.value,
      birth_date: birthDate.value,
      snils: snils.value || null
    }

    await api.post('/patients/', payload)

    // Reset form states and refresh list
    firstName.value = ''
    lastName.value = ''
    birthDate.value = ''
    snils.value = ''
    showModal.value = false

    await fetchChildren()
    alert('Child profile added successfully!')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Failed to register child.'
  }
}

onMounted(() => {
  fetchChildren()
})
</script>

<template>
  <div class="w-full px-4 md:px-8 py-6">
    <!-- Header banner -->
    <div class="flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Parent Dashboard</h1>
        <p class="text-sm text-gray-500">Manage your family's medical profiles</p>
      </div>
      <button
        @click="showModal = true"
        class="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition"
      >
        + Add Child Profile
      </button>
    </div>

    <!-- Global Error Banner -->
    <div v-if="errorMessage" class="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-200">
      {{ errorMessage }}
    </div>

    <!-- CONDITIONAL RENDERING CHAIN START (No comments between adjacent structural divs) -->
    <div v-if="isLoading" class="text-center py-12 text-gray-500 font-medium">
      Loading family profiles...
    </div>

    <div v-else-if="children.length === 0" class="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
      <p class="text-gray-600 font-medium mb-2">No child profiles found</p>
      <p class="text-sm text-gray-400">Click the button above to add your first child profile.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="child in children"
        :key="child.id"
        class="bg-white p-5 rounded-xl border border-gray-200 shadow-xs hover:shadow-md transition"
      >
        <div class="flex items-center space-x-3 mb-3">
          <div class="w-10 h-10 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-bold text-lg">
            {{ child.first_name[0] }}
          </div>
          <div>
            <h3 class="font-bold text-gray-800 text-lg">{{ child.first_name }} {{ child.last_name }}</h3>
            <p class="text-xs text-gray-400">Patient ID: #{{ child.id }}</p>
          </div>
        </div>

        <div class="space-y-1 text-sm text-gray-600 border-t border-gray-100 pt-3">
          <p><strong>Birth Date:</strong> {{ child.birth_date }}</p>
          <p><strong>SNILS:</strong> {{ child.snils || 'Not Provided' }}</p>
        </div>
      </div>
    </div>
    <!-- CONDITIONAL RENDERING CHAIN END -->

    <!-- MODAL POPUP FOR ADDING CHILD -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full p-6 relative">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Register New Child</h2>

        <form @submit.prevent="handleAddChild" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">First Name</label>
            <input v-model="firstName" type="text" required class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Last Name</label>
            <input v-model="lastName" type="text" required class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Birth Date</label>
            <input v-model="birthDate" type="date" required class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">SNILS (Optional)</label>
            <input v-model="snils" type="text" placeholder="123-456-789 00" class="mt-1 w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
          </div>

          <div class="flex space-x-3 pt-2">
            <button
              type="button"
              @click="showModal = false"
              class="w-1/2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="w-1/2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition"
            >
              Save Profile
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
