<template>
  <div class="dashboard">
    <!-- Stat cards -->
    <div class="stats">
      <div class="stat-card stat-card--purple">
        <div class="stat-card__glow"></div>
        <div class="stat-card__content">
          <div class="stat-card__top">
            <div class="stat-card__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span class="stat-card__label">面试次数</span>
          </div>
          <span class="stat-card__value">{{ dashboard?.interview_history?.length || 0 }}</span>
        </div>
      </div>
      <div class="stat-card stat-card--green">
        <div class="stat-card__glow"></div>
        <div class="stat-card__content">
          <div class="stat-card__top">
            <div class="stat-card__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span class="stat-card__label">已完成</span>
          </div>
          <span class="stat-card__value">{{ completedCount }}</span>
        </div>
      </div>
      <div class="stat-card stat-card--blue">
        <div class="stat-card__glow"></div>
        <div class="stat-card__content">
          <div class="stat-card__top">
            <div class="stat-card__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2v6m0 4v6m-6-8h4m4 0h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </div>
            <span class="stat-card__label">技能数</span>
          </div>
          <span class="stat-card__value">{{ topSkills.length }}</span>
        </div>
      </div>
      <div class="stat-card stat-card--warm">
        <div class="stat-card__glow"></div>
        <div class="stat-card__content">
          <div class="stat-card__top">
            <div class="stat-card__icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span class="stat-card__label">学习任务</span>
          </div>
          <span class="stat-card__value">{{ totalQuests }}</span>
        </div>
      </div>
    </div>

    <!-- Main grid -->
    <div class="grid">
      <!-- Skills Overview -->
      <div class="card">
        <div class="card__header">
          <div class="card__header-left">
            <div class="card__header-dot card__header-dot--purple"></div>
            <h3 class="card__title">技能概览</h3>
          </div>
          <router-link to="/app/skills" class="card__link">查看全部</router-link>
        </div>
        <div class="card__body">
          <div v-if="topSkills.length" class="skill-list">
            <div v-for="skill in topSkills" :key="skill.name" class="skill-row">
              <span class="skill-row__name">{{ skill.name }}</span>
              <div class="skill-row__bar">
                <div class="skill-row__fill" :style="{ width: skill.score * 10 + '%', background: scoreGradient(skill.score) }"></div>
              </div>
              <span class="skill-row__score" :style="{ color: scoreColor(skill.score) }">{{ skill.score }}</span>
            </div>
          </div>
          <div v-else class="empty">
            <div class="empty__icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M12 2v6m0 4v6m-6-8h4m4 0h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </div>
            <span class="empty__text">完成面试后自动生成技能评估</span>
          </div>
        </div>
      </div>

      <!-- Quest Progress -->
      <div class="card">
        <div class="card__header">
          <div class="card__header-left">
            <div class="card__header-dot card__header-dot--green"></div>
            <h3 class="card__title">任务进度</h3>
          </div>
          <router-link to="/app/quests" class="card__link">查看全部</router-link>
        </div>
        <div class="card__body">
          <div v-if="dashboard && Object.keys(dashboard.quest_progress).length" class="quest-grid">
            <div v-for="(count, status) in dashboard.quest_progress" :key="status" class="quest-stat" :class="'quest-stat--' + status">
              <span class="quest-stat__count">{{ count }}</span>
              <span class="quest-stat__label">{{ statusLabel(status as string) }}</span>
            </div>
          </div>
          <div v-else class="empty">
            <div class="empty__icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span class="empty__text">暂无学习任务</span>
          </div>
        </div>
      </div>

      <!-- Daily Motivation -->
      <div class="card">
        <div class="card__header">
          <div class="card__header-left">
            <div class="card__header-dot card__header-dot--warm"></div>
            <h3 class="card__title">今日激励</h3>
          </div>
        </div>
        <div class="card__body">
          <div v-if="dashboard?.daily_motivation" class="motivation">
            <div class="motivation__quote">"{{ dashboard.daily_motivation }}"</div>
          </div>
          <p v-else class="motivation__empty">完成一次面试后获得个性化激励</p>
          <div v-if="dashboard?.confidence_score != null" class="confidence">
            <div class="confidence__header">
              <span class="confidence__label">自信指数</span>
              <span class="confidence__value">{{ Math.round((dashboard.confidence_score || 0) * 100) }}%</span>
            </div>
            <div class="confidence__bar">
              <div class="confidence__fill" :style="{ width: Math.round((dashboard.confidence_score || 0) * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interview History -->
    <div class="card card--full">
      <div class="card__header">
        <div class="card__header-left">
          <div class="card__header-dot card__header-dot--blue"></div>
          <h3 class="card__title">面试历史</h3>
        </div>
        <router-link to="/app/interview" class="card__link">开始面试</router-link>
      </div>
      <div class="card__body" v-if="!(dashboard?.interview_history || []).length">
        <div class="empty empty--lg">
          <div class="empty__icon empty__icon--lg">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <span class="empty__title">还没有面试记录</span>
          <span class="empty__text">开始你的第一次 AI 模拟面试，追踪成长轨迹</span>
          <router-link to="/app/interview" class="empty__action">
            <el-button type="primary" round>开始模拟面试</el-button>
          </router-link>
        </div>
      </div>
      <div v-else class="history-list">
        <div v-for="(item, idx) in (dashboard?.interview_history || [])" :key="idx" class="history-item">
          <div class="history-item__left">
            <div class="history-item__avatar" :class="item.status === 'completed' ? 'history-item__avatar--done' : 'history-item__avatar--progress'">
              <svg v-if="item.status === 'completed'" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>
            </div>
            <div class="history-item__info">
              <span class="history-item__time">{{ formatDate(item.created_at) }}</span>
              <span class="history-item__meta">{{ item.question_count || 0 }} 道题目</span>
            </div>
          </div>
          <div class="history-item__right">
            <span v-if="item.overall_score != null" class="score-ring" :class="scoreRingClass(item.overall_score)">
              {{ item.overall_score }}
            </span>
            <span v-else class="score-ring score-ring--na">-</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { growthApi } from '@/api'

const dashboard = ref<any>(null)

const topSkills = computed(() => {
  if (!dashboard.value?.skill_overview) return []
  return dashboard.value.skill_overview
    .filter((s: any) => !s.parent_id)
    .slice(0, 6)
})

const completedCount = computed(() => {
  return (dashboard.value?.interview_history || []).filter((i: any) => i.status === 'completed').length
})

const totalQuests = computed(() => {
  if (!dashboard.value?.quest_progress) return 0
  return Object.values(dashboard.value.quest_progress).reduce((a: number, b: any) => a + (b as number), 0) as number
})

onMounted(async () => {
  try {
    const res = await growthApi.getDashboard()
    dashboard.value = res.data
  } catch { /* empty */ }
})

function scoreGradient(score: number) {
  if (score >= 7) return 'linear-gradient(90deg, #00B894, #55E6C1)'
  if (score >= 4) return 'linear-gradient(90deg, #FDCB6E, #FFE066)'
  return 'linear-gradient(90deg, #FF6B6B, #FF8E8E)'
}

function scoreColor(score: number) {
  if (score >= 7) return '#00B894'
  if (score >= 4) return '#E6A23C'
  return '#FF6B6B'
}

function scoreRingClass(score: number) {
  if (score >= 7) return 'score-ring--high'
  if (score >= 4) return 'score-ring--mid'
  return 'score-ring--low'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    generated: '待开始', in_progress: '进行中', submitted: '已提交', verified_pass: '已通过', verified_fail: '未通过',
  }
  return map[status] || status
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Stat Cards ── */
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  position: relative;
  border-radius: var(--radius-lg);
  padding: 24px;
  overflow: hidden;
  color: #fff;
}

.stat-card--purple { background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%); }
.stat-card--green { background: linear-gradient(135deg, #00B894 0%, #55E6C1 100%); }
.stat-card--blue { background: linear-gradient(135deg, #4A90D9 0%, #74B9FF 100%); }
.stat-card--warm { background: linear-gradient(135deg, #E17055 0%, #FDCB6E 100%); }

.stat-card__glow {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
}

.stat-card__content {
  position: relative;
  z-index: 1;
}

.stat-card__top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.stat-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card__label {
  font-size: 13px;
  font-weight: 500;
  opacity: 0.85;
}

.stat-card__value {
  display: block;
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
}

/* ── Cards ── */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card--full {
  width: 100%;
}

.card__header {
  padding: 18px 22px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card__header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card__header-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.card__header-dot--purple { background: var(--color-primary); }
.card__header-dot--green { background: var(--color-secondary); }
.card__header-dot--blue { background: var(--color-info); }
.card__header-dot--warm { background: var(--color-accent); }

.card__title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
}

.card__link {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-primary);
  text-decoration: none;
  transition: opacity 0.15s;
}

.card__link:hover {
  opacity: 0.7;
}

.card__body {
  padding: 20px 22px;
}

/* ── Skill rows ── */
.skill-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.skill-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.skill-row__name {
  font-size: 13px;
  color: var(--color-text-secondary);
  min-width: 56px;
  flex-shrink: 0;
}

.skill-row__bar {
  flex: 1;
  height: 8px;
  background: var(--color-bg);
  border-radius: 4px;
  overflow: hidden;
}

.skill-row__fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.skill-row__score {
  font-size: 14px;
  font-weight: 800;
  min-width: 24px;
  text-align: right;
}

/* ── Quest Progress ── */
.quest-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quest-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  transition: transform 0.15s ease;
}

.quest-stat:hover {
  transform: translateY(-1px);
}

.quest-stat__count {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text);
  line-height: 1;
  letter-spacing: -0.02em;
}

.quest-stat__label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ── Motivation ── */
.motivation__quote {
  font-size: 15px;
  line-height: 1.7;
  color: var(--color-text-secondary);
  font-style: italic;
  margin-bottom: 20px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #FFF5F9 0%, #FFF8E1 100%);
  border-left: 3px solid var(--color-accent);
}

.motivation__empty {
  color: var(--color-text-muted);
  font-size: 14px;
  margin: 0 0 16px;
}

.confidence__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.confidence__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.confidence__value {
  font-size: 16px;
  font-weight: 800;
  color: var(--color-secondary);
}

.confidence__bar {
  height: 10px;
  background: var(--color-bg);
  border-radius: 5px;
  overflow: hidden;
}

.confidence__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
  border-radius: 5px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Interview History ── */
.history-list {
  padding: 8px 0;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 22px;
  transition: background 0.15s ease;
}

.history-item:hover {
  background: #FAFAFD;
}

.history-item__left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.history-item__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-item__avatar--done {
  background: #E6FAF4;
  color: #00B894;
}

.history-item__avatar--progress {
  background: #FFF5E6;
  color: #FDCB6E;
}

.history-item__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-item__time {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.history-item__meta {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ── Score Ring ── */
.score-ring {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 800;
}

.score-ring--high { background: #E6FAF4; color: #00A381; }
.score-ring--mid { background: #FFF5E6; color: #E6A23C; }
.score-ring--low { background: #FFE8E8; color: #EE5A24; }
.score-ring--na { background: var(--color-bg); color: var(--color-text-muted); }

/* ── Empty state ── */
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
}

.empty--lg {
  padding: 40px 20px;
}

.empty__icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.empty__icon--lg {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: linear-gradient(135deg, #F0EEFF 0%, #E8F4FD 100%);
  color: var(--color-primary);
}

.empty__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.empty__text {
  font-size: 13px;
  color: var(--color-text-muted);
  text-align: center;
}

.empty__action {
  margin-top: 8px;
  text-decoration: none;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
