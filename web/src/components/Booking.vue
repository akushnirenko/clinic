<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api.js'

const patients = ref([])
const doctors = ref([])
const availableSlots = ref([])

// Поля формы
const selectedPatient = ref('')
const selectedDoctor = ref('')
const selectedDate = ref('')
const selectedTime = ref('')
const message = ref('')

// Загрузка детей и врачей при старте
onMounted(async () => {
  try {
    // 1. Загружаем детей родителя
    const ptsRes = await api.get('/patients/')
    patients.value = ptsRes.data

    // 2. Загружаем врачей через правильный эндпоинт со множественным числом 'doctors'
    const docsRes = await api.get('/doctors/all')
    doctors.value = docsRes.data
  } catch (err) {
    console.error('Ошибка загрузки справочников:', err)
  }
})


// Следим за изменением доктора или даты, чтобы обновить слоты времени
watch([selectedDoctor, selectedDate], async () => {
  if (selectedDoctor.value && selectedDate.value) {
    try {
      const res = await api.get('/appointments/available-slots', {
        params: { doctor_id: selectedDoctor.value, date_str: selectedDate.value }
      })
      availableSlots.value = res.data
      selectedTime.value = '' // сбрасываем выбранное время
    } catch (err) {
      console.error('Ошибка загрузки слотов:', err)
    }
  } else {
    availableSlots.value = []
  }
})

const handleBook = async () => {
  try {
    const payload = {
      patient_id: selectedPatient.value,
      doctor_id: selectedDoctor.value,
      appointment_date: selectedDate.value,
      appointment_time: selectedTime.value
    }
    await api.post('/appointments/', payload)
    message.value = 'Запись успешно создана!'
    selectedTime.value = ''
    // Обновляем слоты
    const res = await api.get('/appointments/available-slots', {
      params: { doctor_id: selectedDoctor.value, date_str: selectedDate.value }
    })
    availableSlots.value = res.data
  } catch (err) {
    message.value = err.response?.data?.detail || 'Ошибка при записи'
  }
}
</script>

<template>
  <div class="max-w-xl mx-auto mt-8 p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Онлайн-запись на прием</h2>

    <form @submit.prevent="handleBook" class="space-y-4">
      <!-- Выбор ребенка -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Выбор ребенка</label>
        <select v-model="selectedPatient" required class="mt-1 w-full border border-gray-300 rounded-lg p-2">
          <option value="" disabled>Выберите пациента</option>
          <option v-for="p in patients" :key="p.id" :value="p.id">
            {{ p.first_name }} {{ p.last_name }}
          </option>
        </select>
      </div>

      <!-- Выбор врача -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Врач / Специализация</label>
        <select v-model="selectedDoctor" required class="mt-1 w-full border border-gray-300 rounded-lg p-2">
          <option value="" disabled>Выберите врача</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">
            {{ d.full_name }} ({{ d.specialty }}) — каб. {{ d.room }}
          </option>
        </select>
      </div>

      <!-- Выбор даты -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Дата приема</label>
        <input v-model="selectedDate" type="date" required class="mt-1 w-full border border-gray-300 rounded-lg p-2" />
      </div>

      <!-- Сетка доступного времени -->
      <div v-if="availableSlots.length > 0">
        <label class="block text-sm font-medium text-gray-700 mb-2">Доступное время</label>
        <div class="grid grid-cols-4 gap-2">
          <button
            type="button"
            v-for="slot in availableSlots"
            :key="slot"
            @click="selectedTime = slot"
            :class="selectedTime === slot ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'"
            class="p-2 text-sm font-medium rounded-lg transition"
          >
            {{ slot.substring(0, 5) }}
          </button>
        </div>
      </div>
      <p v-elif="selectedDoctor && selectedDate" class="text-sm text-amber-600">
        Нет доступных слотов на выбранную дату (или у врача выходной).
      </p>

      <!-- Кнопка отправки -->
      <button
        type="submit"
        :disabled="!selectedTime"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition disabled:bg-gray-300"
      >
        Записаться на прием
      </button>
    </form>

    <p v-if="message" class="mt-4 p-3 bg-blue-50 text-blue-700 text-sm rounded-lg text-center font-medium">
      {{ message }}
    </p>
  </div>
</template>
