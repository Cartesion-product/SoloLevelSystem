<template>
  <div class="layout" :class="{ 'layout--collapsed': sidebarCollapsed }">
    <!-- Mobile overlay -->
    <div
      v-if="mobileMenuOpen"
      class="layout__overlay"
      @click="mobileMenuOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar--open': mobileMenuOpen }">
      <div class="sidebar__header">
        <router-link to="/" class="sidebar__logo">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="var(--color-primary)"/>
            <path d="M8 22V10l8 6-8 6zm8-6l8-6v12l-8-6z" fill="#fff"/>
          </svg>
          <span v-if="!sidebarCollapsed" class="sidebar__logo-text">Solo Leveling</span>
        </router-link>
        <button
          v-if="!sidebarCollapsed"
          class="sidebar__collapse-btn"
          @click="sidebarCollapsed = true"
          aria-label="Collapse sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>

      <nav class="sidebar__nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="sidebar__item"
          :class="{ 'sidebar__item--active': isActive(item.path) }"
          @click="mobileMenuOpen = false"
        >
          <span class="sidebar__icon" v-html="item.icon"></span>
          <span v-if="!sidebarCollapsed" class="sidebar__label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar__footer">
        <button
          v-if="sidebarCollapsed"
          class="sidebar__expand-btn"
          @click="sidebarCollapsed = false"
          aria-label="Expand sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <button class="sidebar__logout" @click="handleLogout">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span v-if="!sidebarCollapsed">退出登录</span>
        </button>
      </div>
    </aside>

    <!-- Main area -->
    <div class="main">
      <!-- Mobile top bar -->
      <header class="topbar">
        <button class="topbar__menu-btn" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Open menu">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
        <div class="topbar__avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
      </header>

      <!-- Page hero header -->
      <div class="page-hero" :class="'page-hero--' + currentPageTheme">
        <div class="page-hero__content">
          <div class="page-hero__icon" v-html="currentPageIcon"></div>
          <div class="page-hero__text">
            <h1 class="page-hero__title">{{ currentPageTitle }}</h1>
            <p class="page-hero__desc" v-if="currentPageDesc">{{ currentPageDesc }}</p>
          </div>
        </div>
        <div class="page-hero__decoration">
          <svg width="200" height="120" viewBox="0 0 200 120" fill="none" aria-hidden="true">
            <circle cx="160" cy="60" r="80" fill="currentColor" opacity="0.06"/>
            <circle cx="120" cy="20" r="40" fill="currentColor" opacity="0.04"/>
            <circle cx="180" cy="100" r="30" fill="currentColor" opacity="0.05"/>
          </svg>
        </div>
      </div>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

const navItems = [
  {
    path: '/app',
    label: '成长看板',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 22V12h6v10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  {
    path: '/app/interview',
    label: '模拟面试',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  {
    path: '/app/resumes',
    label: '简历管理',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  {
    path: '/app/jobs',
    label: '目标岗位',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  },
  {
    path: '/app/skills',
    label: '技能树',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2v6m0 4v6m-6-8h4m4 0h4M7 4l2 2m6-2l-2 2M7 20l2-2m6 2l-2-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  },
  {
    path: '/app/quests',
    label: '学习任务',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  {
    path: '/app/knowledge',
    label: '知识库',
    icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
]

interface PageMeta {
  title: string
  desc?: string
  theme: string
  icon: string
}

const pageMeta: Record<string, PageMeta> = {
  '/app': {
    title: '成长看板',
    desc: '追踪你的面试进展和技能成长',
    theme: 'purple',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 22V12h6v10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  '/app/interview': {
    title: '模拟面试',
    desc: 'AI 驱动的实时面试模拟训练',
    theme: 'blue',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  '/app/resumes': {
    title: '简历管理',
    desc: '上传、解析和管理你的简历文档',
    theme: 'green',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  '/app/jobs': {
    title: '目标岗位',
    desc: '设定目标，让 AI 精准匹配你的成长路线',
    theme: 'warm',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  },
  '/app/skills': {
    title: '技能树',
    desc: '可视化技术栈与能力成长轨迹',
    theme: 'purple',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2v6m0 4v6m-6-8h4m4 0h4M7 4l2 2m6-2l-2 2M7 20l2-2m6 2l-2-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  },
  '/app/quests': {
    title: '学习任务',
    desc: '完成任务获取经验值，加速成长进程',
    theme: 'green',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
  '/app/knowledge': {
    title: '知识库',
    desc: '构建个人知识图谱，沉淀学习成果',
    theme: 'blue',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  },
}

const currentPageMeta = computed(() => pageMeta[route.path] || { title: '首页', desc: '', theme: 'purple', icon: '' })
const currentPageTitle = computed(() => currentPageMeta.value.title)
const currentPageDesc = computed(() => currentPageMeta.value.desc || '')
const currentPageTheme = computed(() => currentPageMeta.value.theme)
const currentPageIcon = computed(() => currentPageMeta.value.icon)

function isActive(path: string) {
  if (path === '/app') return route.path === '/app'
  return route.path.startsWith(path)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── Layout Shell ── */
.layout {
  display: flex;
  min-height: 100vh;
}

.layout__overlay {
  display: none;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  background: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.25s ease;
  position: relative;
  z-index: 50;
}

.layout--collapsed .sidebar {
  width: 68px;
}

.sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  min-height: 64px;
}

.sidebar__logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.sidebar__logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
}

.sidebar__collapse-btn,
.sidebar__expand-btn {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sidebar__collapse-btn:hover,
.sidebar__expand-btn:hover {
  color: #fff;
  background: rgba(255,255,255,0.08);
}

/* ── Nav Items ── */
.sidebar__nav {
  flex: 1;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: rgba(255,255,255,0.55);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.layout--collapsed .sidebar__item {
  justify-content: center;
  padding: 10px;
}

.sidebar__item:hover {
  color: rgba(255,255,255,0.9);
  background: rgba(255,255,255,0.06);
}

.sidebar__item--active {
  color: #fff;
  background: var(--color-primary);
}

.sidebar__item--active:hover {
  background: var(--color-primary-dark);
}

.sidebar__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.sidebar__label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Sidebar footer ── */
.sidebar__footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.sidebar__logout {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: none;
  color: rgba(255,255,255,0.45);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.layout--collapsed .sidebar__logout {
  justify-content: center;
  padding: 10px;
}

.sidebar__logout:hover {
  color: var(--color-danger);
  background: rgba(255,107,107,0.1);
}

/* ── Main area ── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--color-bg);
}

/* ── Top bar (mobile-only visible) ── */
.topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 56px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.topbar__menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 6px;
  border-radius: 6px;
}

.topbar__menu-btn:hover {
  background: var(--color-bg);
}

.topbar__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Page Hero Header ── */
.page-hero {
  position: relative;
  padding: 28px 32px;
  overflow: hidden;
  flex-shrink: 0;
}

.page-hero--purple {
  background: linear-gradient(135deg, #6C5CE7 0%, #8B7CF7 50%, #A29BFE 100%);
  color: #fff;
}

.page-hero--green {
  background: linear-gradient(135deg, #00B894 0%, #2ED8A3 50%, #55E6C1 100%);
  color: #fff;
}

.page-hero--blue {
  background: linear-gradient(135deg, #4A90D9 0%, #74B9FF 50%, #A8D8FF 100%);
  color: #fff;
}

.page-hero--warm {
  background: linear-gradient(135deg, #E17055 0%, #FD79A8 50%, #FDCB6E 100%);
  color: #fff;
}

.page-hero__content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.page-hero__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.page-hero__title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.page-hero__desc {
  margin: 4px 0 0;
  font-size: 14px;
  opacity: 0.85;
  font-weight: 400;
}

.page-hero__decoration {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  color: #fff;
  pointer-events: none;
}

/* ── Content area ── */
.content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 260px !important;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 200;
  }

  .sidebar--open {
    transform: translateX(0);
  }

  .layout__overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 199;
  }

  .topbar {
    display: flex;
  }

  .page-hero {
    padding: 20px 16px;
  }

  .page-hero__title {
    font-size: 18px;
  }

  .page-hero__icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
  }

  .page-hero__decoration {
    display: none;
  }

  .content {
    padding: 16px;
  }
}
</style>
