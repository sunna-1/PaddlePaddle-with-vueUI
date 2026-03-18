import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './views/HomePage.vue'
import AnalysisPage from './views/AnalysisPage.vue'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/analysis', name: 'Analysis', component: AnalysisPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
