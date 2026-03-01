<template>
  <div class="interview">
    <!-- Pre-interview setup -->
    <div v-if="!interviewStore.isSessionActive && !interviewStore.sessionId" class="setup">
      <div class="setup__card">
        <div class="setup__icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
        <h2 class="setup__title">开始模拟面试</h2>
        <p class="setup__desc">选择简历和岗位，AI 面试官将为你量身定制面试问题</p>

        <el-form label-position="top" class="setup__form">
          <el-form-item label="选择简历">
            <el-select v-model="selectedResume" placeholder="默认使用默认简历" clearable size="large" style="width:100%">
              <el-option v-for="r in resumes" :key="r.id" :label="r.title" :value="r.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标岗位">
            <el-select v-model="selectedJob" placeholder="默认使用默认岗位" clearable size="large" style="width:100%">
              <el-option v-for="j in jobs" :key="j.id" :label="j.position_name" :value="j.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="面试题数">
            <el-input-number v-model="maxQuestions" :min="3" :max="20" size="large" />
          </el-form-item>
          <el-button type="primary" :loading="starting" @click="handleStart" size="large" class="setup__btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            开始面试
          </el-button>
        </el-form>
      </div>
    </div>

    <!-- Chat interface -->
    <div v-else class="chat">
      <div class="chat__header">
        <div class="chat__meta">
          <el-tag round size="small">{{ interviewStore.metadata.phase || 'defense' }}</el-tag>
          <el-tag round type="info" size="small">难度: {{ interviewStore.metadata.difficulty || 'medium' }}</el-tag>
          <el-tag round type="warning" size="small">题目: {{ interviewStore.metadata.question_count || 0 }}</el-tag>
        </div>
        <el-button v-if="interviewStore.isSessionActive" type="danger" size="small" round @click="handleEnd">
          结束面试
        </el-button>
      </div>

      <div class="chat__messages" ref="messagesContainer">
        <div
          v-for="(msg, idx) in interviewStore.messages"
          :key="idx"
          class="msg"
          :class="'msg--' + msg.role"
        >
          <div class="msg__avatar" :class="'msg__avatar--' + msg.role">
            {{ msg.role === 'assistant' ? 'AI' : '我' }}
          </div>
          <div class="msg__bubble" :class="'msg__bubble--' + msg.role">
            <div class="msg__text">{{ msg.content }}</div>
          </div>
        </div>
        <div v-if="interviewStore.isStreaming && !lastMessageHasContent" class="msg msg--assistant">
          <div class="msg__avatar msg__avatar--assistant">AI</div>
          <div class="msg__bubble msg__bubble--assistant">
            <div class="typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat__input" v-if="interviewStore.isSessionActive">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          placeholder="输入你的回答... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="handleSend"
          :disabled="interviewStore.isStreaming"
        />
        <el-button
          type="primary"
          :loading="interviewStore.isStreaming"
          @click="handleSend"
          :disabled="!inputMessage.trim()"
          class="chat__send-btn"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </el-button>
      </div>

      <!-- Report -->
      <div v-if="!interviewStore.isSessionActive && interviewStore.metadata.report" class="report">
        <div class="report__header">
          <h3 class="report__title">面试报告</h3>
          <div class="report__actions">
            <el-button size="small" round @click="handleDownloadTranscript">
              下载面试记录
            </el-button>
            <div class="report__score-ring">
              <span class="report__score-value">{{ interviewStore.metadata.report.overall_score ?? '-' }}</span>
              <span class="report__score-unit">/10</span>
            </div>
          </div>
        </div>
        <div class="report__body">
          <div class="report__stat">
            <span class="report__stat-label">题目数</span>
            <span class="report__stat-value">{{ interviewStore.metadata.report.question_count }}</span>
          </div>
          <div v-if="interviewStore.metadata.report.strengths?.length" class="report__section">
            <span class="report__section-title report__section-title--success">亮点</span>
            <div class="report__tags">
              <el-tag v-for="s in interviewStore.metadata.report.strengths" :key="s" type="success" round size="small">{{ s }}</el-tag>
            </div>
          </div>
          <div v-if="interviewStore.metadata.report.gap_list?.length" class="report__section">
            <span class="report__section-title report__section-title--danger">待提升</span>
            <div class="report__tags">
              <el-tag v-for="g in interviewStore.metadata.report.gap_list" :key="g" type="danger" round size="small">{{ g }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useInterviewStore } from '@/stores/interview'
import { resumeApi, jobApi, interviewApi } from '@/api'

const interviewStore = useInterviewStore()

const resumes = ref<any[]>([])
const jobs = ref<any[]>([])
const selectedResume = ref('')
const selectedJob = ref('')
const maxQuestions = ref(8)
const starting = ref(false)
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()

const lastMessageHasContent = computed(() => {
  const msgs = interviewStore.messages
  if (msgs.length === 0) return false
  const last = msgs[msgs.length - 1]
  return last.role === 'assistant' && last.content.length > 0
})

onMounted(async () => {
  interviewStore.reset()
  try {
    const [rRes, jRes] = await Promise.all([resumeApi.list(), jobApi.list()])
    resumes.value = rRes.data.resumes || []
    jobs.value = jRes.data.jobs || []
  } catch { /* empty */ }
})

watch(() => interviewStore.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})

async function handleStart() {
  starting.value = true
  try {
    await interviewStore.startSession(
      selectedResume.value || undefined,
      selectedJob.value || undefined,
      maxQuestions.value,
    )
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '启动面试失败')
  } finally {
    starting.value = false
  }
}

async function handleSend() {
  const msg = inputMessage.value.trim()
  if (!msg) return
  inputMessage.value = ''
  await interviewStore.sendMessage(msg)
}

async function handleEnd() {
  await interviewStore.endSession()
  ElMessage.info('面试已结束')
}

async function handleDownloadTranscript() {
  try {
    const res = await interviewApi.downloadTranscript(interviewStore.sessionId)
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `interview_${interviewStore.sessionId.slice(0, 8)}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载面试记录失败')
  }
}
</script>

<style scoped>
.interview {
  height: calc(100vh - 112px);
  display: flex;
  flex-direction: column;
}

/* ── Setup ── */
.setup {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.setup__card {
  width: 100%;
  max-width: 520px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl, 20px);
  padding: 48px 40px;
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.setup__icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 8px 24px rgba(108, 92, 231, 0.3);
}

.setup__title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.setup__desc {
  margin: 0 0 32px;
  font-size: 15px;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.setup__form {
  text-align: left;
}

.setup__form :deep(.el-form-item__label) {
  font-weight: 600;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.setup__btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}

/* ── Chat ── */
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  flex-shrink: 0;
}

.chat__meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chat__messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Messages ── */
.msg {
  display: flex;
  gap: 10px;
  max-width: 80%;
}

.msg--user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg--assistant {
  align-self: flex-start;
}

.msg__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.msg__avatar--assistant {
  background: var(--color-primary);
  color: #fff;
}

.msg__avatar--user {
  background: var(--color-secondary);
  color: #fff;
}

.msg__bubble {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.6;
  font-size: 14px;
}

.msg__bubble--assistant {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-bottom-left-radius: 4px;
}

.msg__bubble--user {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg__text {
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Input ── */
.chat__input {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  padding: 12px 0;
  flex-shrink: 0;
  border-top: 1px solid var(--color-border);
}

.chat__input .el-textarea {
  flex: 1;
}

.chat__send-btn {
  height: 40px;
  width: 40px;
  padding: 0;
  border-radius: 10px;
  flex-shrink: 0;
}

/* ── Report ── */
.report {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-top: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.report__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.report__title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.report__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report__score-ring {
  display: flex;
  align-items: baseline;
}

.report__score-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-primary);
}

.report__score-unit {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-left: 2px;
}

.report__body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report__stat {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.report__stat-label { color: var(--color-text-muted); }
.report__stat-value { font-weight: 600; color: var(--color-text); }

.report__section-title {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.report__section-title--success { color: var(--color-secondary); }
.report__section-title--danger { color: var(--color-danger); }

.report__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* ── Typing indicator ── */
.typing {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing span {
  width: 7px;
  height: 7px;
  background: var(--color-text-muted);
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}
</style>
