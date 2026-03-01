<template>
  <div class="page">
    <div class="page__toolbar">
      <div class="page__count">
        <span class="page__count-num">{{ documents.length }}</span> 篇文档
      </div>
      <el-upload :show-file-list="false" :before-upload="handleUpload" accept=".pdf,.docx,.doc,.txt,.md">
        <el-button type="primary" round>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right:6px"><path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          上传文档
        </el-button>
      </el-upload>
    </div>

    <!-- Card grid -->
    <div v-if="documents.length" class="card-grid" v-loading="loading">
      <div v-for="doc in documents" :key="doc.id" class="item-card" @click="viewDetail(doc)">
        <div class="item-card__header">
          <div class="item-card__icon item-card__icon--blue">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <el-tag :type="statusType(doc.status)" size="small" round>{{ statusLabel(doc.status) }}</el-tag>
        </div>
        <h3 class="item-card__title">{{ doc.doc_name }}</h3>
        <div class="item-card__meta">
          <span v-if="doc.doc_type">{{ doc.doc_type }}</span>
          <span v-if="doc.chunk_count">{{ doc.chunk_count }} 个切片</span>
        </div>
        <div v-if="doc.domain_tags?.length" class="item-card__tags">
          <el-tag v-for="t in doc.domain_tags" :key="t" size="small" round>{{ t }}</el-tag>
        </div>
        <!-- Error message for failed docs -->
        <div v-if="doc.status === 'failed' && doc.error_message" class="item-card__error">
          {{ doc.error_message }}
        </div>
        <div class="item-card__actions" @click.stop>
          <el-button size="small" type="danger" text @click="handleDelete(doc.id)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-state__icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <h3 class="empty-state__title">知识库为空</h3>
      <p class="empty-state__desc">上传技术文档、笔记或博客，AI 将自动索引用于面试准备</p>
      <el-upload :show-file-list="false" :before-upload="handleUpload" accept=".pdf,.docx,.doc,.txt,.md">
        <el-button type="primary" round>上传第一篇文档</el-button>
      </el-upload>
    </div>

    <!-- Upload config dialog -->
    <el-dialog v-model="showUploadDialog" title="上传知识文档" width="440px">
      <el-form label-position="top">
        <el-form-item label="类型">
          <el-select v-model="uploadForm.doc_type" size="large" style="width:100%">
            <el-option label="技术书籍" value="tech_book" />
            <el-option label="面试笔记" value="interview_note" />
            <el-option label="博客文章" value="blog" />
            <el-option label="八股文" value="bagua" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadForm.domain_tags" placeholder="逗号分隔，如: redis,分布式" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false" round>取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload" round>上传</el-button>
      </template>
    </el-dialog>

    <!-- Document Detail Drawer -->
    <el-drawer v-model="showDetailDrawer" :title="docDetail?.document.doc_name || '文档详情'" size="600px" destroy-on-close>
      <div v-loading="detailLoading" class="detail-container">
        <template v-if="docDetail">
          <div class="detail-header">
            <div class="detail-stat">
              <span class="detail-stat__label">状态</span>
              <el-tag :type="statusType(docDetail.document.status)" size="small" round>{{ statusLabel(docDetail.document.status) }}</el-tag>
            </div>
            <div class="detail-stat">
              <span class="detail-stat__label">切片总数</span>
              <span class="detail-stat__value">{{ docDetail.document.chunk_count }}</span>
            </div>
             <div class="detail-stat">
              <span class="detail-stat__label">上传时间</span>
              <span class="detail-stat__value">{{ new Date(docDetail.document.created_at).toLocaleString() }}</span>
            </div>
          </div>

          <!-- Failed status detail -->
          <el-alert v-if="docDetail.document.status === 'failed'" type="error" show-icon :closable="false" style="margin-bottom: 20px;">
            <p style="word-break: break-all; margin: 0;">{{ docDetail.document.error_message }}</p>
          </el-alert>

          <!-- Warning if no chunks available yet -->
          <el-alert v-else-if="docDetail.document.status !== 'ready' && docDetail.document.status !== 'failed'"
                    type="info" show-icon :closable="false" style="margin-bottom: 20px;">
            文档正在处理中，切片数据将在状态变为“就绪”后可见。
          </el-alert>
          <el-alert v-else-if="docDetail.document.status === 'ready' && docDetail.chunks.length === 0"
                    type="warning" show-icon :closable="false" style="margin-bottom: 20px;">
            该文档未提取到任何有效的文本切片数据。
          </el-alert>

          <!-- Chunk Timeline View -->
          <div v-if="docDetail.chunks.length > 0" class="chunk-list-header">
            <h4>文本切片预览</h4>
          </div>
          
          <el-scrollbar>
            <el-timeline style="padding-left: 4px; padding-top: 10px;">
              <el-timeline-item
                v-for="(chunk, index) in docDetail.chunks"
                :key="chunk.id"
                :timestamp="`Sequence #${index + 1}`"
                placement="top"
                type="primary"
                hollow
              >
                <el-card class="chunk-card" shadow="hover">
                  <p class="chunk-content">{{ chunk.content }}</p>
                  <div class="chunk-footer">
                    <span>UUID: {{ chunk.id }}</span>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-scrollbar>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '@/api'

const documents = ref<any[]>([])
const loading = ref(false)
const showUploadDialog = ref(false)
const uploading = ref(false)
const pendingFile = ref<File | null>(null)
const uploadForm = ref({ doc_type: 'tech_book', domain_tags: '' })

// Detail Drawer States
const showDetailDrawer = ref(false)
const detailLoading = ref(false)
const docDetail = ref<any>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadDocs()
})

onUnmounted(() => {
  stopPolling()
})

async function loadDocs() {
  loading.value = true
  try {
    const res = await knowledgeApi.list()
    documents.value = res.data.documents || []
    startPollingIfNeeded()
  } finally {
    loading.value = false
  }
}

// ── Status Polling ──────────────────────────────────────────
function startPollingIfNeeded() {
  const processingDocs = documents.value.filter(d => d.status !== 'ready' && d.status !== 'failed')
  if (processingDocs.length > 0 && !pollTimer) {
    pollTimer = setInterval(pollStatuses, 2000)
  } else if (processingDocs.length === 0) {
    stopPolling()
  }
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollStatuses() {
  const processingDocs = documents.value.filter(d => d.status !== 'ready' && d.status !== 'failed')
  if (processingDocs.length === 0) {
    stopPolling()
    return
  }

  for (const doc of processingDocs) {
    try {
      const res = await knowledgeApi.getStatus(doc.id)
      const statusData = res.data
      if (statusData.status !== doc.status) {
        doc.status = statusData.status
        doc.error_message = statusData.error_message
        doc.chunk_count = statusData.chunk_count

        if (statusData.status === 'ready') {
          ElMessage.success(`${doc.doc_name} 处理完成`)
        } else if (statusData.status === 'failed') {
          ElMessage.error(`${doc.doc_name} 处理失败: ${statusData.error_message || '未知错误'}`)
        }
      }
    } catch {
      // Silently ignore individual poll failures
    }
  }

  startPollingIfNeeded()
}

// ── Upload ──────────────────────────────────────────────────
function handleUpload(file: File) {
  pendingFile.value = file
  showUploadDialog.value = true
  return false
}

async function confirmUpload() {
  if (!pendingFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', pendingFile.value)
    fd.append('doc_type', uploadForm.value.doc_type)
    fd.append('domain_tags', uploadForm.value.domain_tags)
    await knowledgeApi.upload(fd)
    ElMessage.success('文档上传成功，正在后台处理...')
    showUploadDialog.value = false
    await loadDocs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// ── Detail Drawer ───────────────────────────────────────────
async function viewDetail(doc: any) {
  showDetailDrawer.value = true
  detailLoading.value = true
  docDetail.value = null
  try {
    const res = await knowledgeApi.getDetail(doc.id)
    docDetail.value = res.data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '获取详情失败')
    showDetailDrawer.value = false
  } finally {
    detailLoading.value = false
  }
}

// ── Delete ──────────────────────────────────────────────────
async function handleDelete(id: string) {
  await ElMessageBox.confirm('删除后文档及其向量数据将不可恢复', '确认删除')
  try {
    await knowledgeApi.delete(id)
    ElMessage.success('已删除')
    await loadDocs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

// ── Status helpers ──────────────────────────────────────────
function statusType(status: string) {
  const map: Record<string, string> = { 
    ready: 'success', 
    failed: 'danger' 
  }
  return map[status] || 'warning'
}

function statusLabel(status: string) {
  const map: Record<string, string> = { 
    pending: '等待处理',
    processing: '处理中', // Fallback for old records
    parsing: '解析文档中', 
    chunking: '文本分块中', 
    vectorizing: '大模型向量化中', 
    storing: '写入数据库中', 
    ready: '就绪', 
    failed: '失败' 
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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
  align-items: center;
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

.item-card__icon--blue {
  background: linear-gradient(135deg, #E8F4FD 0%, #D6ECFD 100%);
  color: #4A90D9;
}

.item-card__title {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
  word-break: break-word;
}

.item-card__meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 12px;
}

.item-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.item-card__error {
  font-size: 12px;
  color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 12px;
  line-height: 1.4;
  word-break: break-word;
}

.item-card__actions {
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
  background: linear-gradient(135deg, #E8F4FD 0%, #F0EEFF 100%);
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

/* ── Detail Drawer ── */
.detail-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  gap: 20px;
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
}

.detail-stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-stat__label {
  font-size: 12px;
  color: var(--color-text-muted);
}

.detail-stat__value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.chunk-list-header {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.chunk-list-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}

.chunk-card {
  --el-card-padding: 12px 16px;
  border-radius: var(--radius-md);
}

.chunk-content {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
}

.chunk-footer {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: monospace;
  display: flex;
  justify-content: flex-end;
}
</style>
