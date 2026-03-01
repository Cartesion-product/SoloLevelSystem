<template>
  <div class="auth">
    <!-- Left branding panel -->
    <div class="auth__brand">
      <div class="auth__brand-inner">
        <router-link to="/" class="auth__logo">
          <svg width="36" height="36" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="#fff"/>
            <path d="M8 22V10l8 6-8 6zm8-6l8-6v12l-8-6z" fill="#6C5CE7"/>
          </svg>
          <span>Solo Leveling</span>
        </router-link>

        <h1 class="auth__headline">像打怪升级一样<br/>攻克每一场面试</h1>
        <p class="auth__tagline">
          AI 驱动的面试辅导平台，游戏化的技能成长体系，
          帮助你系统提升面试能力。
        </p>

        <div class="auth__features">
          <div class="auth__feature">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>AI 实时模拟面试</span>
          </div>
          <div class="auth__feature">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M3 3v18h18M7 16l4-4 4 4 5-5" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>数据驱动成长看板</span>
          </div>
          <div class="auth__feature">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2v6m0 4v6m-6-8h4m4 0h4" stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round"/></svg>
            <span>可视化技能树系统</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="auth__form-panel">
      <div class="auth__form-wrapper">
        <router-link to="/" class="auth__back">
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
            <path d="M16 10H4m0 0l4-4m-4 4l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回首页
        </router-link>

        <div class="auth__form-header">
          <!-- Mobile-only logo -->
          <div class="auth__mobile-logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="#6C5CE7"/>
              <path d="M8 22V10l8 6-8 6zm8-6l8-6v12l-8-6z" fill="#fff"/>
            </svg>
          </div>
          <h2 class="auth__form-title">{{ activeTab === 'login' ? '欢迎回来' : '创建账号' }}</h2>
          <p class="auth__form-desc">{{ activeTab === 'login' ? '登录你的账号，继续升级之旅' : '注册一个新账号，开始你的升级之旅' }}</p>
        </div>

        <el-tabs v-model="activeTab" class="auth__tabs">
          <el-tab-pane label="登录" name="login">
            <el-form @submit.prevent="handleLogin" class="auth__form">
              <el-form-item>
                <el-input v-model="loginForm.email" placeholder="邮箱地址" prefix-icon="Message" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password size="large" />
              </el-form-item>
              <el-button type="primary" :loading="loading" @click="handleLogin" size="large" class="auth__submit">
                登录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form @submit.prevent="handleRegister" class="auth__form">
              <el-form-item>
                <el-input v-model="registerForm.username" placeholder="用户名" prefix-icon="User" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.email" placeholder="邮箱地址" prefix-icon="Message" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.password" type="password" placeholder="密码 (至少6位)" prefix-icon="Lock" show-password size="large" />
              </el-form-item>
              <el-button type="primary" :loading="loading" @click="handleRegister" size="large" class="auth__submit">
                创建账号
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <p class="auth__footer-text">
          注册即表示同意我们的服务条款和隐私政策
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({ email: '1804806181@qq.com', password: '123123' })
const registerForm = ref({ username: '', email: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(loginForm.value.email, loginForm.value.password)
    ElMessage.success('登录成功')
    router.push('/app')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  try {
    await authStore.register(registerForm.value.username, registerForm.value.email, registerForm.value.password)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.value.email = registerForm.value.email
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth {
  display: flex;
  min-height: 100vh;
}

/* ── Left branding panel ── */
.auth__brand {
  flex: 0 0 45%;
  background: linear-gradient(135deg, #1A1A2E 0%, #2D2B55 50%, #3D1F72 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  position: relative;
  overflow: hidden;
}

.auth__brand::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(108,92,231,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.auth__brand::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(253,121,168,0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.auth__brand-inner {
  position: relative;
  z-index: 1;
  max-width: 420px;
}

.auth__logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  margin-bottom: 48px;
}

.auth__logo span {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.auth__headline {
  font-size: 36px;
  line-height: 1.2;
  color: #fff;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.auth__tagline {
  font-size: 16px;
  line-height: 1.7;
  color: rgba(255,255,255,0.6);
  margin: 0 0 40px;
}

.auth__features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth__feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  font-weight: 500;
}

/* ── Right form panel ── */
.auth__form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  background: var(--color-surface);
}

.auth__form-wrapper {
  width: 100%;
  max-width: 400px;
}

.auth__back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  margin-bottom: 32px;
  transition: color 0.2s;
}

.auth__back:hover {
  color: var(--color-primary);
}

.auth__mobile-logo {
  display: none;
  margin-bottom: 16px;
}

.auth__form-header {
  margin-bottom: 28px;
}

.auth__form-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 8px;
}

.auth__form-desc {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

.auth__tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.auth__tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--color-border);
}

.auth__tabs :deep(.el-tabs__active-bar) {
  height: 2px;
}

.auth__tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
}

.auth__form .el-form-item {
  margin-bottom: 20px;
}

.auth__submit {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
}

.auth__footer-text {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 24px 0 0;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .auth {
    flex-direction: column;
  }

  .auth__brand {
    display: none;
  }

  .auth__mobile-logo {
    display: block;
  }

  .auth__form-panel {
    padding: 32px 20px;
    min-height: 100vh;
    background: linear-gradient(180deg, #F0EEFF 0%, var(--color-surface) 30%);
  }

  .auth__form-wrapper {
    max-width: 420px;
  }
}
</style>
