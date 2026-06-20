import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <-- Import your router configuration
import './assets/main.css'

const app = createApp(App)

app.use(router) // <-- Tell Vue to use Vue Router navigation plugins

app.mount('#app')
