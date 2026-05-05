import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PromptBuilderWizard from '@/components/PromptBuilderWizard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path : '/prompt_view',
      name : 'prompt',
      component : PromptBuilderWizard
    }
  ],
})

export default router
