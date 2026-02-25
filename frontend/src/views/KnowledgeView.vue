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
      <div v-for="doc in documents" :key="doc.id" class="item-card">
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
        <div class="item-card__actions">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '@/api'

const documents = ref<any[]>([])
const loading = ref(false)
const showUploadDialog = ref(false)
const uploading = ref(false)
const pendingFile = ref<File | null>(null)
const uploadForm = ref({ doc_type: 'tech_book', domain_tags: '' })

onMounted(() => loadDocs())

async function loadDocs() {
  loading.value = true
  try {
    const res = await knowledgeApi.list()
    documents.value = res.data.documents || []
  } finally {
    loading.value = false
  }
}

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
    ElMessage.success('文档上传成功，正在处理中...')
    showUploadDialog.value = false
    await loadDocs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('删除后文档及其向量数据将不可恢复', '确认删除')
  await knowledgeApi.delete(id)
  ElMessage.success('已删除')
  await loadDocs()
}

function statusType(status: string) {
  const map: Record<string, string> = { processing: 'warning', ready: 'success', failed: 'danger' }
  return map[status] || 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = { processing: '处理中', ready: '就绪', failed: '失败' }
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
</style>
