<template>
  <div class="page">
    <div class="page__toolbar">
      <div class="page__count">
        <span class="page__count-num">{{ quests.length }}</span> 个任务
      </div>
      <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="loadQuests" style="width:160px">
        <el-option label="全部" value="" />
        <el-option label="待开始" value="generated" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已提交" value="submitted" />
        <el-option label="已通过" value="verified_pass" />
        <el-option label="未通过" value="verified_fail" />
      </el-select>
    </div>

    <!-- Quest cards -->
    <div v-if="quests.length" class="card-grid" v-loading="loading">
      <div v-for="quest in quests" :key="quest.id" class="quest-card" :class="'quest-card--' + quest.status">
        <div class="quest-card__header">
          <div class="quest-card__icon" :class="'quest-card__icon--' + statusColor(quest.status)">
            <svg v-if="quest.status === 'verified_pass'" width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else-if="quest.status === 'verified_fail'" width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else-if="quest.status === 'in_progress'" width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <el-tag :type="statusTagType(quest.status)" size="small" round>{{ statusLabel(quest.status) }}</el-tag>
        </div>
        <h3 class="quest-card__title">{{ quest.quest_title }}</h3>
        <p class="quest-card__detail">{{ quest.quest_detail }}</p>
        <div class="quest-card__footer">
          <el-tag v-if="quest.verification_method" size="small" round type="info">{{ quest.verification_method }}</el-tag>
          <div class="quest-card__actions">
            <el-button
              v-if="quest.status === 'generated'"
              size="small" type="primary" round
              @click="updateStatus(quest.id, 'in_progress')"
            >开始</el-button>
            <el-button
              v-if="quest.status === 'in_progress'"
              size="small" type="success" round
              @click="updateStatus(quest.id, 'submitted')"
            >提交</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-state__icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <h3 class="empty-state__title">还没有学习任务</h3>
      <p class="empty-state__desc">完成面试后 AI 将自动生成个性化学习任务</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { questApi } from '@/api'

const quests = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref('')

onMounted(() => loadQuests())

async function loadQuests() {
  loading.value = true
  try {
    const res = await questApi.list(statusFilter.value || undefined)
    quests.value = res.data.quests || []
  } finally {
    loading.value = false
  }
}

async function updateStatus(id: string, status: string) {
  await questApi.updateStatus(id, status)
  ElMessage.success('状态已更新')
  await loadQuests()
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    generated: 'info', in_progress: 'warning', submitted: '', verified_pass: 'success', verified_fail: 'danger',
  }
  return map[status] || 'info'
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    generated: 'gray', in_progress: 'blue', submitted: 'purple', verified_pass: 'green', verified_fail: 'red',
  }
  return map[status] || 'gray'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    generated: '待开始', in_progress: '进行中', submitted: '已提交', verified_pass: '已通过', verified_fail: '未通过',
  }
  return map[status] || status
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page__count {
  font-size: 14px;
  color: var(--color-text-muted);
}

.page__count-num {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text);
  margin-right: 4px;
}

/* ── Card Grid ── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.quest-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--shadow-xs);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.quest-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.quest-card--verified_pass {
  border-left: 3px solid var(--color-secondary);
}

.quest-card--verified_fail {
  border-left: 3px solid var(--color-danger);
}

.quest-card--in_progress {
  border-left: 3px solid var(--color-info);
}

.quest-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.quest-card__icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quest-card__icon--green { background: #E6FAF4; color: #00B894; }
.quest-card__icon--red { background: #FFE8E8; color: #FF6B6B; }
.quest-card__icon--blue { background: #E8F4FD; color: #4A90D9; }
.quest-card__icon--purple { background: var(--color-primary-bg); color: var(--color-primary); }
.quest-card__icon--gray { background: var(--color-bg); color: var(--color-text-muted); }

.quest-card__title {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.4;
}

.quest-card__detail {
  margin: 0 0 16px;
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.quest-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
}

.quest-card__actions {
  display: flex;
  gap: 6px;
}

/* ── Empty State ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state__icon {
  width: 80px;
  height: 80px;
  border-radius: 24px;
  background: linear-gradient(135deg, #E6FAF4 0%, #F0EEFF 100%);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-state__title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
}

.empty-state__desc {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-muted);
  max-width: 320px;
}
</style>
