import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: () => import('@/views/LandingView.vue'),
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/app',
      component: () => import('@/views/LayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'resumes',
          name: 'Resumes',
          component: () => import('@/views/ResumesView.vue'),
        },
        {
          path: 'jobs',
          name: 'Jobs',
          component: () => import('@/views/JobsView.vue'),
        },
        {
          path: 'interview',
          name: 'Interview',
          component: () => import('@/views/InterviewView.vue'),
        },
        {
          path: 'skills',
          name: 'Skills',
          component: () => import('@/views/SkillsView.vue'),
        },
        {
          path: 'quests',
          name: 'Quests',
          component: () => import('@/views/QuestsView.vue'),
        },
        {
          path: 'knowledge',
          name: 'Knowledge',
          component: () => import('@/views/KnowledgeView.vue'),
        },
      ],
    },
  ],
})

// Route guard
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return { name: 'Login' }
  }
  if (to.name === 'Login' && token) {
    return { name: 'Dashboard' }
  }
})

export default router
