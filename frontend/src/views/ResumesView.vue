<template>
  <div class="page">
    <div class="page__toolbar">
      <div class="page__count">
        <span class="page__count-num">{{ resumes.length }}</span> 份简历
      </div>
      <el-upload :show-file-list="false" :before-upload="handleUpload" accept=".pdf,.docx,.doc">
        <el-button type="primary" round>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right:6px"><path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          上传简历
        </el-button>
      </el-upload>
    </div>

    <!-- Card grid -->
    <div v-if="resumes.length" class="card-grid" v-loading="loading">
      <div v-for="resume in resumes" :key="resume.id" class="item-card">
        <div class="item-card__header">
          <div class="item-card__icon item-card__icon--green">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div class="item-card__badges">
            <span v-if="resume.is_default" class="badge badge--primary">默认</span>
            <el-tag v-if="resume.parsing_status === 'parsing'" type="primary" size="small" round>
              <el-icon class="is-loading" style="margin-right: 4px;"><Loading /></el-icon>
              解析中
            </el-tag>
            <el-tag v-else-if="resume.parsing_status === 'completed'" type="success" size="small" round>已完成</el-tag>
            <el-tag v-else-if="resume.parsing_status === 'failed'" type="danger" size="small" round>失败</el-tag>
          </div>
        </div>
        <h3 class="item-card__title">{{ resume.title || '未命名简历' }}</h3>
        <div class="item-card__meta">
          <span>{{ resume.template_type || '通用' }}</span>
          <span>{{ new Date(resume.created_at).toLocaleDateString('zh-CN') }}</span>
        </div>
        <div class="item-card__actions">
          <el-button size="small" round @click="showDetail(resume)" :disabled="resume.parsing_status === 'parsing'">查看</el-button>
          <el-button size="small" round @click="handleSetDefault(resume.id)" :disabled="resume.is_default">设为默认</el-button>
          <el-button size="small" type="danger" text @click="handleDelete(resume.id)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-state__icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <h3 class="empty-state__title">还没有上传简历</h3>
      <p class="empty-state__desc">上传简历后 AI 将自动解析并生成技能评估</p>
      <el-upload :show-file-list="false" :before-upload="handleUpload" accept=".pdf,.docx,.doc">
        <el-button type="primary" round>上传第一份简历</el-button>
      </el-upload>
    </div>

    <!-- Detail dialog -->
    <el-dialog v-model="showDialog" title="简历详情" width="60%">
      <pre class="code-block">{{ JSON.stringify(selectedResume?.parsed_data, null, 2) }}</pre>
    </el-dialog>

    <!-- Upload dialog -->
    <el-dialog v-model="showUploadDialog" title="上传简历" width="440px">
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="uploadForm.title" placeholder="简历标题" size="large" />
        </el-form-item>
        <el-form-item label="模板">
          <el-select v-model="uploadForm.template_type" size="large" style="width:100%">
            <el-option label="AI开发" value="ai_dev" />
            <el-option label="后端开发" value="backend" />
            <el-option label="全栈开发" value="fullstack" />
            <el-option label="数据工程" value="data" />
            <el-option label="通用" value="generic" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false" round>取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload" round>确认上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { resumeApi } from '@/api'

const resumes = ref<any[]>([])
const loading = ref(false)
const showDialog = ref(false)
const selectedResume = ref<any>(null)
const showUploadDialog = ref(false)
const uploading = ref(false)
const pendingFile = ref<File | null>(null)
const uploadForm = ref({ title: '', template_type: 'generic' })
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => loadResumes())
onUnmounted(() => stopPolling())

watch(resumes, (list) => {
  const hasParsing = list.some((r: any) => r.parsing_status === 'parsing')
  if (hasParsing && !pollTimer) {
    startPolling()
  } else if (!hasParsing && pollTimer) {
    stopPolling()
  }
}, { deep: true })

function startPolling() {
  if (pollTimer) return
  pollTimer = setInterval(() => {
    loadResumes(true)
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function loadResumes(silent = false) {
  if (!silent) loading.value = true
  try {
    const res = await resumeApi.list()
    resumes.value = res.data.resumes || []
  } finally {
    if (!silent) loading.value = false
  }
}

function handleUpload(file: File) {
  pendingFile.value = file
  uploadForm.value.title = file.name
  showUploadDialog.value = true
  return false
}

async function confirmUpload() {
  if (!pendingFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', pendingFile.value)
    fd.append('title', uploadForm.value.title)
    fd.append('template_type', uploadForm.value.template_type)
    await resumeApi.upload(fd)
    ElMessage.success('简历已上传，正在后台解析...')
    showUploadDialog.value = false
    await loadResumes()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

function showDetail(resume: any) {
  selectedResume.value = resume
  showDialog.value = true
}

async function handleSetDefault(id: string) {
  await resumeApi.setDefault(id)
  ElMessage.success('已设为默认')
  await loadResumes()
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确认删除此简历？', '提示')
  await resumeApi.delete(id)
  ElMessage.success('已删除')
  await loadResumes()
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.item-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--shadow-xs);
  transition: all 0.2s ease;
}

.item-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.item-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.item-card__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-card__icon--green {
  background: linear-gradient(135deg, #E6FAF4 0%, #CCF5E9 100%);
  color: #00B894;
}

.item-card__badges {
  display: flex;
  gap: 6px;
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.badge--primary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.item-card__title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.item-card__meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 16px;
}

.item-card__actions {
  display: flex;
  gap: 6px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
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
  margin: 0 0 20px;
  font-size: 14px;
  color: var(--color-text-muted);
  max-width: 320px;
}

.code-block {
  background: var(--color-bg);
  padding: 16px;
  border-radius: var(--radius-sm);
  overflow: auto;
  max-height: 500px;
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  margin: 0;
}
</style>
