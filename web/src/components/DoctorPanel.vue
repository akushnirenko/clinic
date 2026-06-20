<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api.js'

// Справочники и списки
const doctors = ref([])
const appointments = ref([])

// Состояние интерфейса
const selectedDoctor = ref('')
const selectedDate = ref(new Date().toISOString().split('T')[0]) // Текущая дата по умолчанию
const activeAppointment = ref(null) // Пациент, которого принимаем прямо сейчас

// Поля формы приема
const complaints = ref('')
const diagnosis = ref('')
const treatmentPlan = ref('')
const message = ref('')

// Загрузка списка врачей для авторизации/выбора панели
onMounted(async () => {
  try {
    const res = await api.get('/doctors/all')
    doctors.value = res.data
  } catch (err) {
    console.error('Ошибка загрузки врачей:', err)
  }
})

// Загрузка журнала записей врача на выбранную дату
const fetchJournal = async () => {
  if (!selectedDoctor.value || !selectedDate.value) return
  try {
    const res = await api.get('/doctors/journal', {
      params: { doctor_id: selectedDoctor.value, date_str: selectedDate.value }
    })
    appointments.value = res.data
  } catch (err) {
    console.error('Ошибка загрузки журнала:', err)
  }
}

// Следим за изменением врача или даты, чтобы обновлять расписание
watch([selectedDoctor, selectedDate], fetchJournal)

// Открытие экрана приема конкретного ребенка
const startConsultation = (appt) => {
  activeAppointment.value = appt
  complaints.value = ''
  diagnosis.value = ''
  treatmentPlan.value = ''
  message.value = ''
}

// Отправка данных осмотра на бэкенд
const submitConsultation = async () => {
  try {
    const payload = {
      patient_id: activeAppointment.value.patient_id,
      doctor_id: selectedDoctor.value,
      appointment_id: activeAppointment.value.id,
      visit_date: selectedDate.value,
      complaints: complaints.value,
      diagnosis: diagnosis.value,
      treatment_plan: treatmentPlan.value
    }

    await api.post('/doctors/consultation', payload)
    message.value = 'Прием успешно завершен, данные занесены в медкарту!'
    activeAppointment.value = null
    await fetchJournal() // Обновляем статус в списке на "completed"
  } catch (err) {
    message.value = 'Ошибка при сохранении карты приема.'
  }
}
</script>

<template>
  <div class="w-full px-4 md:px-8 py-6">
    <div class="bg-white border border-gray-200 rounded-xl p-6 shadow-xs mb-6 flex flex-col md:flex-row gap-4 justify-between items-center">
      <div>
        <h1 class="text-xl font-bold text-gray-800">🩺 Рабочее место врача</h1>
        <p class="text-xs text-gray-400">Выберите врача для симуляции входа в личный кабинет сотрудника</p>
      </div>

      <div class="flex gap-3 w-full md:w-auto">
        <!-- Селектор врача -->
        <select v-model="selectedDoctor" class="border border-gray-300 rounded-lg p-2 text-sm bg-gray-50">
          <option value="" disabled>-- Выберите врача --</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">
            {{ d.full_name }} ({{ d.specialty }})
          </option>
        </select>

        <!-- Календарь журнала -->
        <input v-model="selectedDate" type="date" class="border border-gray-300 rounded-lg p-2 text-sm bg-gray-50" />
      </div>
    </div>

    <!-- ОСНОВНОЙ РАБОЧИЙ ИНТЕРФЕЙС (Отображается, когда врач выбран) -->
    <div v-if="selectedDoctor" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- ЛЕВАЯ КОЛОНКА: ЖУРНАЛ ЗАПИСЕЙ -->
      <div class="lg:col-span-1 bg-white border border-gray-200 rounded-xl p-4 shadow-xs">
        <h2 class="font-bold text-gray-700 mb-3 border-b border-gray-100 pb-2">📋 Журнал записей</h2>

        <div v-if="appointments.length === 0" class="text-center py-8 text-sm text-gray-400">
          На эту дату записей нет.
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="appt in appointments"
            :key="appt.id"
            :class="appt.status === 'completed' ? 'border-green-200 bg-green-50/50' : 'border-gray-200 hover:border-blue-300'"
            class="p-3 border rounded-lg transition flex justify-between items-center"
          >
            <div>
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-sm mr-2">
                {{ appt.appointment_time.substring(0, 5) }}
              </span>
              <span class="text-sm font-medium text-gray-800">Пациент ID: #{{ appt.patient_id }}</span>
              <p class="text-xs text-gray-400 mt-1">Статус: {{ appt.status }}</p>
            </div>

            <button
              v-if="appt.status !== 'completed'"
              @click="startConsultation(appt)"
              class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-2.5 py-1.5 rounded-md transition"
            >
              Принять
            </button>
          </div>
        </div>
      </div>

      <!-- ПРАВАЯ КОЛОНКА: СТРАНИЦА ПРИЕМА (ЭЛЕКТРОННАЯ МЕДКАРТА) -->
      <div class="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-xs">
        <div v-if="activeAppointment">
          <h2 class="font-bold text-gray-800 text-lg mb-4 border-b border-gray-100 pb-2 flex justify-between">
            <span>🩺 Приём пациента (ID: #{{ activeAppointment.patient_id }})</span>
            <span class="text-sm text-blue-600 font-normal">Время записи: {{ activeAppointment.appointment_time.substring(0, 5) }}</span>
          </h2>

          <form @submit.prevent="submitConsultation" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Жалобы пациента</label>
              <textarea v-model="complaints" required rows="3" placeholder="Опишите симптомы, температуру, кашель..." class="mt-1 w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-blue-500"></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Диагноз</label>
              <input v-model="diagnosis" type="text" required placeholder="Например: ОРВИ, Острый бронхит, Здоров" class="mt-1 w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">План лечения и рекомендации (Необязательно)</label>
              <textarea v-model="treatmentPlan" rows="3" placeholder="Препараты, дозировка, домашний режим..." class="mt-1 w-full border border-gray-300 rounded-lg p-2 text-sm focus:outline-blue-500"></textarea>
            </div>

            <div class="flex gap-3 pt-2">
              <button type="button" @click="activeAppointment = null" class="w-1/3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg text-sm transition">
                Отмена
              </button>
              <button type="submit" class="w-2/3 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded-lg text-sm transition shadow-xs">
                Сохранить в медкарту и завершить прием
              </button>
            </div>
          </form>
        </div>

        <div v-else class="h-full flex flex-col items-center justify-center py-16 text-gray-400">
          <p v-if="message" class="mb-4 p-3 bg-green-50 text-green-700 text-sm rounded-lg font-medium border border-green-100">{{ message }}</p>
          <span class="text-4xl mb-2">🧑‍⚕️</span>
          <p class="text-sm font-medium">Нет активного приема</p>
          <p class="text-xs text-gray-400 mt-1">Выберите пациента из левого журнала записей, чтобы начать осмотр.</p>
        </div>
      </div>

    </div>

    <!-- ЗАГЛУШКА: ЕСЛИ ВРАЧ НЕ ВЫБРАН -->
    <div v-else class="text-center py-16 bg-white border border-gray-200 rounded-xl shadow-xs text-gray-400">
      <span class="text-4xl">👨‍⚕️</span>
      <p class="text-sm font-medium mt-2">Кабинет врача пуст</p>
      <p class="text-xs text-gray-400 mt-1">Пожалуйста, выберите специалиста в верхнем выпадающем меню для загрузки его рабочего журнала.</p>
    </div>
  </div>
</template>
