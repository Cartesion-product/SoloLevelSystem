<template>
  <div class="landing">
    <!-- Navigation -->
    <nav class="nav" :class="{ 'nav--scrolled': isScrolled }" role="navigation" aria-label="主导航">
      <div class="container nav__inner">
        <a href="/" class="nav__logo" aria-label="Solo Leveling System 首页">
          <svg class="nav__logo-icon" width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect width="32" height="32" rx="8" fill="currentColor"/>
            <path d="M8 22V10l8 6-8 6zm8-6l8-6v12l-8-6z" fill="#fff"/>
          </svg>
          <span class="nav__logo-text">Solo Leveling</span>
        </a>

        <button
          class="nav__toggle"
          :class="{ 'nav__toggle--open': mobileMenuOpen }"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-expanded="mobileMenuOpen"
          aria-controls="nav-menu"
          aria-label="切换导航菜单"
        >
          <span></span><span></span><span></span>
        </button>

        <div id="nav-menu" class="nav__menu" :class="{ 'nav__menu--open': mobileMenuOpen }">
          <a href="#features" class="nav__link" @click="closeMenu">功能</a>
          <a href="#how-it-works" class="nav__link" @click="closeMenu">工作流程</a>
          <a href="#testimonials" class="nav__link" @click="closeMenu">用户评价</a>
          <a href="#pricing" class="nav__link" @click="closeMenu">定价</a>
          <div class="nav__actions">
            <router-link to="/login" class="btn btn--ghost btn--sm" @click="closeMenu">登录</router-link>
            <router-link to="/login" class="btn btn--primary btn--sm" @click="closeMenu">免费开始</router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="container hero__inner">
        <div class="hero__content">
          <div class="hero__badge">AI 驱动 · 游戏化成长</div>
          <h1 class="hero__title">
            像打怪升级一样<br/>
            <span class="hero__highlight">攻克每一场面试</span>
          </h1>
          <p class="hero__subtitle">
            Solo Leveling System 将 AI 面试教练、技能树、成长看板融为一体。
            用游戏化的方式系统提升你的面试能力，从求职新人蜕变为 Offer 收割机。
          </p>
          <div class="hero__cta">
            <router-link to="/login" class="btn btn--primary btn--lg">
              免费开始升级
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </router-link>
            <a href="#how-it-works" class="btn btn--outline btn--lg">了解工作流程</a>
          </div>
          <p class="hero__note">无需信用卡 · 永久免费基础版</p>
        </div>
        <div class="hero__visual" aria-hidden="true">
          <div class="hero__card hero__card--main">
            <div class="hero__card-header">
              <span class="hero__card-dot hero__card-dot--green"></span>
              <span class="hero__card-dot hero__card-dot--yellow"></span>
              <span class="hero__card-dot hero__card-dot--red"></span>
            </div>
            <div class="hero__card-body">
              <div class="hero__card-avatar">AI</div>
              <div class="hero__card-bubble">
                请介绍一个你主导的技术项目，遇到了什么挑战？
              </div>
            </div>
            <div class="hero__card-body hero__card-body--user">
              <div class="hero__card-bubble hero__card-bubble--user">
                我负责了微服务架构迁移，将单体应用拆分为 12 个服务...
              </div>
              <div class="hero__card-avatar hero__card-avatar--user">你</div>
            </div>
            <div class="hero__card-score">
              <span class="hero__card-score-label">面试评分</span>
              <div class="hero__card-score-bar">
                <div class="hero__card-score-fill"></div>
              </div>
              <span class="hero__card-score-value">92/100</span>
            </div>
          </div>
          <div class="hero__card hero__card--float hero__card--skills">
            <div class="hero__card-skill">
              <span>系统设计</span>
              <div class="hero__skill-bar"><div class="hero__skill-fill" style="width:85%"></div></div>
            </div>
            <div class="hero__card-skill">
              <span>算法</span>
              <div class="hero__skill-bar"><div class="hero__skill-fill" style="width:72%"></div></div>
            </div>
            <div class="hero__card-skill">
              <span>行为面试</span>
              <div class="hero__skill-bar"><div class="hero__skill-fill" style="width:90%"></div></div>
            </div>
          </div>
          <div class="hero__card hero__card--float hero__card--level">
            <span class="hero__level-badge">LV.27</span>
            <span class="hero__level-text">高级猎人</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Strip -->
    <section class="trust" aria-label="平台数据">
      <div class="container">
        <div class="trust__grid">
          <div class="trust__item">
            <span class="trust__number">10,000+</span>
            <span class="trust__label">注册用户</span>
          </div>
          <div class="trust__divider" aria-hidden="true"></div>
          <div class="trust__item">
            <span class="trust__number">50,000+</span>
            <span class="trust__label">模拟面试</span>
          </div>
          <div class="trust__divider" aria-hidden="true"></div>
          <div class="trust__item">
            <span class="trust__number">85%</span>
            <span class="trust__label">面试通过率</span>
          </div>
          <div class="trust__divider" aria-hidden="true"></div>
          <div class="trust__item">
            <span class="trust__number">4.9/5</span>
            <span class="trust__label">用户评分</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="features section">
      <div class="container">
        <div class="section__header">
          <span class="section__tag">核心功能</span>
          <h2 class="section__title">六大武器，助你升级通关</h2>
          <p class="section__desc">从面试模拟到知识管理，全方位覆盖求职全链路</p>
        </div>
        <div class="features__grid">
          <div class="feature-card" v-for="feature in features" :key="feature.title">
            <div class="feature-card__icon" :style="{ background: feature.bg }">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" v-html="feature.icon"></svg>
            </div>
            <h3 class="feature-card__title">{{ feature.title }}</h3>
            <p class="feature-card__desc">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how-it-works" class="steps section">
      <div class="container">
        <div class="section__header">
          <span class="section__tag">快速上手</span>
          <h2 class="section__title">三步开始你的升级之旅</h2>
        </div>
        <div class="steps__grid">
          <div class="step" v-for="(step, i) in steps" :key="i">
            <div class="step__number">{{ i + 1 }}</div>
            <h3 class="step__title">{{ step.title }}</h3>
            <p class="step__desc">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section id="testimonials" class="testimonials section">
      <div class="container">
        <div class="section__header">
          <span class="section__tag">用户评价</span>
          <h2 class="section__title">他们已经成功升级</h2>
        </div>
        <div class="testimonials__grid">
          <article class="testimonial" v-for="t in testimonials" :key="t.name">
            <div class="testimonial__stars" aria-label="5星评价">
              <svg v-for="n in 5" :key="n" width="16" height="16" viewBox="0 0 16 16" fill="#F59E0B" aria-hidden="true">
                <path d="M8 0l2.47 5.01L16 5.81l-4 3.9.94 5.49L8 12.49l-4.94 2.71L4 9.71 0 5.81l5.53-.8z"/>
              </svg>
            </div>
            <blockquote class="testimonial__quote">{{ t.quote }}</blockquote>
            <div class="testimonial__author">
              <div class="testimonial__avatar" :style="{ background: t.color }">{{ t.name[0] }}</div>
              <div>
                <div class="testimonial__name">{{ t.name }}</div>
                <div class="testimonial__role">{{ t.role }}</div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="pricing section">
      <div class="container">
        <div class="section__header">
          <span class="section__tag">灵活定价</span>
          <h2 class="section__title">选择适合你的升级方案</h2>
          <p class="section__desc">所有方案均包含核心功能，随时可以升级或取消</p>
        </div>
        <div class="pricing__grid">
          <div class="price-card" v-for="plan in plans" :key="plan.name" :class="{ 'price-card--featured': plan.featured }">
            <div class="price-card__badge" v-if="plan.featured">最受欢迎</div>
            <h3 class="price-card__name">{{ plan.name }}</h3>
            <div class="price-card__price">
              <span class="price-card__amount">{{ plan.price }}</span>
              <span class="price-card__period" v-if="plan.period">/{{ plan.period }}</span>
            </div>
            <p class="price-card__desc">{{ plan.desc }}</p>
            <ul class="price-card__features">
              <li v-for="f in plan.features" :key="f">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M3 8l3.5 3.5L13 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                {{ f }}
              </li>
            </ul>
            <router-link to="/login" class="btn btn--lg" :class="plan.featured ? 'btn--primary' : 'btn--outline'" style="width:100%">
              {{ plan.cta }}
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="final-cta">
      <div class="container final-cta__inner">
        <h2 class="final-cta__title">准备好开始你的升级之旅了吗？</h2>
        <p class="final-cta__desc">加入 10,000+ 求职者的行列，用 AI 的力量系统提升面试能力。</p>
        <router-link to="/login" class="btn btn--white btn--lg">
          免费注册，立即升级
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer" role="contentinfo">
      <div class="container">
        <div class="footer__grid">
          <div class="footer__brand">
            <div class="nav__logo" style="margin-bottom:12px">
              <svg class="nav__logo-icon" width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <rect width="32" height="32" rx="8" fill="var(--color-primary)"/>
                <path d="M8 22V10l8 6-8 6zm8-6l8-6v12l-8-6z" fill="#fff"/>
              </svg>
              <span class="nav__logo-text">Solo Leveling</span>
            </div>
            <p class="footer__tagline">AI 智能面试辅导平台<br/>像打怪升级一样攻克每一场面试</p>
          </div>
          <div class="footer__links">
            <h4>产品</h4>
            <a href="#features">核心功能</a>
            <a href="#pricing">定价方案</a>
            <a href="#how-it-works">工作流程</a>
          </div>
          <div class="footer__links">
            <h4>支持</h4>
            <a href="#">帮助中心</a>
            <a href="#">联系我们</a>
            <a href="#">常见问题</a>
          </div>
          <div class="footer__links">
            <h4>法律</h4>
            <a href="#">隐私政策</a>
            <a href="#">服务条款</a>
            <a href="#">Cookie 政策</a>
          </div>
        </div>
        <div class="footer__bottom">
          <p>&copy; {{ new Date().getFullYear() }} Solo Leveling System. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isScrolled = ref(false)
const mobileMenuOpen = ref(false)

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function closeMenu() {
  mobileMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const features = [
  {
    title: 'AI 模拟面试',
    desc: '基于 GPT 的实时对话面试官，覆盖技术面、行为面、系统设计等多种场景，即时反馈评分。',
    bg: 'rgba(108,92,231,0.1)',
    icon: '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="#6C5CE7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    title: '技能树系统',
    desc: '可视化展示你的技术栈全景，AI 自动评估薄弱环节，生成个性化学习路径。',
    bg: 'rgba(0,184,148,0.1)',
    icon: '<path d="M12 2v6m0 4v6m-6-8h4m4 0h4M7 4l2 2m6-2l-2 2M7 20l2-2m6 2l-2-2" stroke="#00B894" stroke-width="2" stroke-linecap="round"/>'
  },
  {
    title: '成长看板',
    desc: '追踪面试次数、通过率、信心指数等核心指标，用数据驱动你的成长。',
    bg: 'rgba(253,121,168,0.1)',
    icon: '<path d="M3 3v18h18M7 16l4-4 4 4 5-5" stroke="#FD79A8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    title: '简历管理',
    desc: '上传简历自动解析，AI 提取关键信息，匹配目标岗位要求，一键优化简历。',
    bg: 'rgba(9,132,227,0.1)',
    icon: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="#0984E3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8" stroke="#0984E3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    title: '学习任务',
    desc: '将备面计划拆解为可执行的每日任务（Quest），完成任务获取经验值，持续升级。',
    bg: 'rgba(255,159,67,0.1)',
    icon: '<path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="#FF9F43" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  },
  {
    title: '知识库',
    desc: '上传面经、技术文档，构建个人知识图谱。AI 基于知识库回答面试问题。',
    bg: 'rgba(162,155,254,0.1)',
    icon: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z" stroke="#A29BFE" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
  }
]

const steps = [
  {
    title: '创建账号，上传简历',
    desc: 'AI 自动解析你的简历信息和技术栈，建立初始技能档案。'
  },
  {
    title: '开始模拟面试',
    desc: '选择目标岗位，AI 面试官根据 JD 和你的简历量身定制面试问题。'
  },
  {
    title: '追踪成长，持续升级',
    desc: '查看面试评分报告，完成学习任务，看着你的等级不断提升。'
  }
]

const testimonials = [
  {
    name: '张伟',
    role: '前端工程师 · 拿到字节跳动 Offer',
    quote: '用了两周 Solo Leveling，模拟面试让我提前适应了高压环境。最终面试时完全不紧张，顺利拿到了心仪的 Offer。',
    color: '#6C5CE7'
  },
  {
    name: '李静',
    role: '后端开发 · 成功转行大厂',
    quote: '技能树功能太棒了，让我清楚看到自己哪些地方需要补强。AI 的即时反馈比自己刷题高效 10 倍。',
    color: '#00B894'
  },
  {
    name: '王浩',
    role: '应届生 · 斩获 3 个 SP Offer',
    quote: '作为应届生，之前完全不知道怎么准备面试。这个系统像一个私人教练，一步步带我从小白升级到面试达人。',
    color: '#FD79A8'
  }
]

const plans = [
  {
    name: '免费版',
    price: '¥0',
    period: '',
    desc: '开始探索你的升级之旅',
    features: ['每月 5 次 AI 模拟面试', '基础技能树', '成长看板', '1 份简历管理'],
    cta: '免费开始',
    featured: false
  },
  {
    name: '专业版',
    price: '¥49',
    period: '月',
    desc: '适合正在积极求职的你',
    features: ['无限次 AI 模拟面试', '完整技能树 + AI 建议', '详细面试报告', '无限简历管理', '学习任务系统', '知识库 (10GB)'],
    cta: '升级专业版',
    featured: true
  },
  {
    name: '团队版',
    price: '¥199',
    period: '月',
    desc: '适合培训机构和团队',
    features: ['专业版全部功能', '最多 20 个成员', '团队数据看板', '自定义面试题库', '专属客服支持', 'API 访问'],
    cta: '联系销售',
    featured: false
  }
]
</script>

<style scoped>
/* ========= Design Tokens ========= */
:root {
  --color-primary: #6C5CE7;
  --color-primary-dark: #5A4BD1;
  --color-primary-light: #A29BFE;
  --color-secondary: #00B894;
  --color-secondary-dark: #00A381;
  --color-accent: #FD79A8;
  --color-text: #1A1A2E;
  --color-text-secondary: #4A4A68;
  --color-text-muted: #7C7C96;
  --color-bg: #FAFBFF;
  --color-surface: #FFFFFF;
  --color-border: #E8E8F0;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
  --shadow-xl: 0 16px 48px rgba(0,0,0,0.16);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

/* ========= Reset & Base ========= */
*,
*::before,
*::after {
  box-sizing: border-box;
}

.landing {
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.6;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ========= Typography ========= */
h1, h2, h3, h4 {
  margin: 0;
  line-height: 1.2;
  font-weight: 700;
}

p {
  margin: 0;
}

a {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s;
}

/* ========= Buttons ========= */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: inherit;
  font-weight: 600;
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn--sm {
  padding: 8px 18px;
  font-size: 14px;
}

.btn--lg {
  padding: 14px 28px;
  font-size: 16px;
}

.btn--primary {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.btn--primary:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108,92,231,0.35);
}

.btn--outline {
  background: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn--outline:hover {
  background: var(--color-primary);
  color: #fff;
}

.btn--ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border-color: transparent;
}

.btn--ghost:hover {
  color: var(--color-primary);
}

.btn--white {
  background: #fff;
  color: var(--color-primary);
  border-color: #fff;
}

.btn--white:hover {
  background: #f0edff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* ========= Navigation ========= */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 16px 0;
  transition: all 0.3s ease;
  background: transparent;
}

.nav--scrolled {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 8px rgba(0,0,0,0.06);
  padding: 10px 0;
}

.nav__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav__logo {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.nav__logo-icon {
  color: var(--color-primary);
}

.nav__logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
}

.nav__toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  z-index: 101;
}

.nav__toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--color-text);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.nav__toggle--open span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.nav__toggle--open span:nth-child(2) {
  opacity: 0;
}

.nav__toggle--open span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.nav__menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav__link {
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.nav__link:hover {
  color: var(--color-primary);
}

.nav__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ========= Hero ========= */
.hero {
  padding: 140px 0 80px;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 30%, #e0f2fe 100%);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(108,92,231,0.08) 0%, transparent 70%);
  border-radius: 50%;
}

.hero__inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero__badge {
  display: inline-block;
  padding: 6px 16px;
  background: rgba(108,92,231,0.1);
  color: var(--color-primary);
  border-radius: 100px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 20px;
}

.hero__title {
  font-size: 48px;
  line-height: 1.15;
  color: var(--color-text);
  margin-bottom: 20px;
  letter-spacing: -0.02em;
}

.hero__highlight {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero__subtitle {
  font-size: 18px;
  line-height: 1.7;
  color: var(--color-text-secondary);
  margin-bottom: 32px;
  max-width: 520px;
}

.hero__cta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.hero__note {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* Hero visual - mockup cards */
.hero__visual {
  position: relative;
  height: 420px;
}

.hero__card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 16px;
}

.hero__card--main {
  position: absolute;
  top: 0;
  left: 0;
  right: 20px;
  z-index: 2;
}

.hero__card-header {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.hero__card-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.hero__card-dot--red { background: #FF6B6B; }
.hero__card-dot--yellow { background: #FFD93D; }
.hero__card-dot--green { background: #6BCB77; }

.hero__card-body {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: flex-start;
}

.hero__card-body--user {
  justify-content: flex-end;
}

.hero__card-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.hero__card-avatar--user {
  background: var(--color-secondary);
}

.hero__card-bubble {
  background: #f3f4f6;
  padding: 10px 14px;
  border-radius: 12px 12px 12px 2px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  max-width: 280px;
}

.hero__card-bubble--user {
  background: var(--color-primary);
  color: #fff;
  border-radius: 12px 12px 2px 12px;
}

.hero__card-score {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
  margin-top: 4px;
}

.hero__card-score-label {
  font-size: 12px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.hero__card-score-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.hero__card-score-fill {
  width: 92%;
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  border-radius: 3px;
}

.hero__card-score-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-secondary);
}

.hero__card--float {
  position: absolute;
  z-index: 3;
  animation: float 6s ease-in-out infinite;
}

.hero__card--skills {
  bottom: 20px;
  left: -10px;
  width: 200px;
  animation-delay: -2s;
}

.hero__card--level {
  top: 50px;
  right: -10px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  animation-delay: -4s;
}

.hero__card-skill {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.hero__card-skill:last-child {
  margin-bottom: 0;
}

.hero__card-skill span {
  width: 56px;
  flex-shrink: 0;
  font-weight: 500;
}

.hero__skill-bar {
  flex: 1;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.hero__skill-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
}

.hero__level-badge {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: #fff;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 800;
}

.hero__level-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* ========= Trust Strip ========= */
.trust {
  padding: 48px 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.trust__grid {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.trust__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.trust__number {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.trust__label {
  font-size: 14px;
  color: var(--color-text-muted);
}

.trust__divider {
  width: 1px;
  height: 40px;
  background: var(--color-border);
}

/* ========= Sections ========= */
.section {
  padding: 96px 0;
}

.section__header {
  text-align: center;
  margin-bottom: 56px;
}

.section__tag {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(108,92,231,0.08);
  color: var(--color-primary);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 16px;
}

.section__title {
  font-size: 36px;
  color: var(--color-text);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.section__desc {
  font-size: 17px;
  color: var(--color-text-secondary);
  max-width: 560px;
  margin: 0 auto;
}

/* ========= Features ========= */
.features {
  background: var(--color-bg);
}

.features__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 32px 28px;
  transition: all 0.25s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

.feature-card__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-card__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 10px;
}

.feature-card__desc {
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

/* ========= Steps ========= */
.steps {
  background: var(--color-surface);
}

.steps__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  position: relative;
}

.steps__grid::before {
  content: '';
  position: absolute;
  top: 28px;
  left: 15%;
  right: 15%;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  opacity: 0.2;
}

.step {
  text-align: center;
  position: relative;
}

.step__number {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  font-size: 22px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  position: relative;
  z-index: 1;
}

.step__title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--color-text);
}

.step__desc {
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-text-secondary);
  max-width: 280px;
  margin: 0 auto;
}

/* ========= Testimonials ========= */
.testimonials {
  background: var(--color-bg);
}

.testimonials__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.testimonial {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 28px;
  transition: all 0.25s ease;
}

.testimonial:hover {
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

.testimonial__stars {
  display: flex;
  gap: 2px;
  margin-bottom: 16px;
}

.testimonial__quote {
  font-size: 15px;
  line-height: 1.7;
  color: var(--color-text-secondary);
  margin: 0 0 20px;
  font-style: normal;
}

.testimonial__author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.testimonial__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.testimonial__name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.testimonial__role {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ========= Pricing ========= */
.pricing {
  background: var(--color-surface);
}

.pricing__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  align-items: start;
}

.price-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 36px 28px;
  position: relative;
  transition: all 0.25s ease;
}

.price-card:hover {
  box-shadow: var(--shadow-md);
}

.price-card--featured {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-lg);
  transform: scale(1.03);
}

.price-card--featured:hover {
  box-shadow: var(--shadow-xl);
}

.price-card__badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 16px;
  background: var(--color-primary);
  color: #fff;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.price-card__name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--color-text);
}

.price-card__price {
  margin-bottom: 8px;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price-card__amount {
  font-size: 40px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.price-card__period {
  font-size: 15px;
  color: var(--color-text-muted);
}

.price-card__desc {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-bottom: 24px;
}

.price-card__features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
}

.price-card__features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--color-text-secondary);
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.price-card__features li:last-child {
  border-bottom: none;
}

.price-card__features li svg {
  color: var(--color-secondary);
  flex-shrink: 0;
}

/* ========= Final CTA ========= */
.final-cta {
  padding: 80px 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, #4834d4 100%);
}

.final-cta__inner {
  text-align: center;
}

.final-cta__title {
  font-size: 36px;
  color: #fff;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.final-cta__desc {
  font-size: 17px;
  color: rgba(255,255,255,0.8);
  margin-bottom: 32px;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

/* ========= Footer ========= */
.footer {
  background: #1A1A2E;
  padding: 64px 0 0;
  color: rgba(255,255,255,0.7);
}

.footer__grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  padding-bottom: 48px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.footer__brand .nav__logo-text {
  color: #fff;
}

.footer__tagline {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255,255,255,0.5);
}

.footer__links h4 {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16px;
}

.footer__links a {
  display: block;
  font-size: 14px;
  color: rgba(255,255,255,0.5);
  padding: 6px 0;
  transition: color 0.2s;
}

.footer__links a:hover {
  color: #fff;
}

.footer__bottom {
  padding: 24px 0;
  text-align: center;
}

.footer__bottom p {
  font-size: 13px;
  color: rgba(255,255,255,0.35);
}

/* ========= Responsive ========= */
@media (max-width: 1024px) {
  .hero__title {
    font-size: 40px;
  }

  .section__title {
    font-size: 30px;
  }

  .features__grid,
  .testimonials__grid,
  .pricing__grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .steps__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }

  .footer__grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
}

@media (max-width: 768px) {
  .nav__toggle {
    display: flex;
  }

  .nav__menu {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 280px;
    background: var(--color-surface);
    flex-direction: column;
    align-items: flex-start;
    padding: 80px 24px 24px;
    gap: 8px;
    box-shadow: var(--shadow-xl);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }

  .nav__menu--open {
    transform: translateX(0);
  }

  .nav__link {
    font-size: 16px;
    padding: 10px 0;
    width: 100%;
  }

  .nav__actions {
    flex-direction: column;
    width: 100%;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-border);
  }

  .nav__actions .btn {
    width: 100%;
  }

  .hero {
    padding: 120px 0 60px;
  }

  .hero__inner {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .hero__title {
    font-size: 32px;
  }

  .hero__subtitle {
    font-size: 16px;
  }

  .hero__visual {
    height: 360px;
    max-width: 400px;
    margin: 0 auto;
  }

  .hero__card--main {
    right: 10px;
  }

  .hero__card--skills {
    left: -5px;
    bottom: 10px;
    width: 170px;
  }

  .hero__card--level {
    right: -5px;
    top: 40px;
  }

  .trust__grid {
    gap: 24px;
  }

  .trust__number {
    font-size: 22px;
  }

  .trust__divider {
    display: none;
  }

  .section {
    padding: 64px 0;
  }

  .features__grid,
  .testimonials__grid {
    grid-template-columns: 1fr;
  }

  .steps__grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .steps__grid::before {
    display: none;
  }

  .pricing__grid {
    grid-template-columns: 1fr;
    max-width: 400px;
    margin: 0 auto;
  }

  .price-card--featured {
    transform: none;
  }

  .final-cta {
    padding: 56px 0;
  }

  .final-cta__title {
    font-size: 26px;
  }

  .footer__grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 16px;
  }

  .hero__title {
    font-size: 28px;
  }

  .hero__cta {
    flex-direction: column;
  }

  .hero__cta .btn {
    width: 100%;
  }

  .trust__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .section__title {
    font-size: 24px;
  }

  .price-card__amount {
    font-size: 32px;
  }
}
</style>
