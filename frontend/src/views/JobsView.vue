<template>
  <div class="page">
    <div class="page__toolbar">
      <div class="page__count">
        <span class="page__count-num">{{ jobs.length }}</span> 个岗位
      </div>
      <el-button type="primary" round @click="showCreate = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right:6px"><path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        新增岗位
      </el-button>
    </div>

    <!-- Card grid -->
    <div v-if="jobs.length" class="card-grid" v-loading="loading">
      <div v-for="job in jobs" :key="job.id" class="item-card">
        <div class="item-card__header">
          <div class="item-card__icon item-card__icon--warm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </div>
          <div class="item-card__badges">
            <span v-if="job.is_default" class="badge badge--primary">默认</span>
          </div>
        </div>
        <h3 class="item-card__title">{{ job.position_name }}</h3>
        <p class="item-card__subtitle" v-if="job.company_name">{{ job.company_name }}</p>
        <div class="item-card__tags" v-if="job.parsed_requirements?.required_skills?.length">
          <el-tag v-for="s in job.parsed_requirements.required_skills.slice(0, 4)" :key="s" size="small" round>{{ s }}</el-tag>
          <el-tag v-if="job.parsed_requirements.required_skills.length > 4" size="small" round type="info">+{{ job.parsed_requirements.required_skills.length - 4 }}</el-tag>
        </div>
        <div class="item-card__actions">
          <el-button size="small" round @click="showDetail(job)">查看</el-button>
          <el-button size="small" round @click="handleSetDefault(job.id)" :disabled="job.is_default">设为默认</el-button>
          <el-button size="small" type="danger" text @click="handleDelete(job.id)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-state__icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </div>
      <h3 class="empty-state__title">还没有添加目标岗位</h3>
      <p class="empty-state__desc">添加目标岗位后 AI 将为你定制面试方案和学习路线</p>
      <el-button type="primary" round @click="showCreate = true">添加第一个岗位</el-button>
    </div>

    <!-- Create dialog -->
    <el-dialog v-model="showCreate" title="新增目标岗位" width="600px">
      <el-form label-position="top">
        <el-form-item label="公司名称">
          <el-input v-model="form.company_name" placeholder="公司名称（可选）" size="large" />
        </el-form-item>
        <el-form-item label="职位名称">
          <el-input v-model="form.position_name" placeholder="职位名称" size="large" />
        </el-form-item>
        <el-form-item label="JD 内容">
          <el-input v-model="form.jd_text" type="textarea" :rows="10" placeholder="粘贴岗位 JD 全文..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false" round>取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate" round>创建</el-button>
      </template>
    </el-dialog>

    <!-- Detail / Edit dialog -->
    <el-dialog v-model="showDetailDialog" title="岗位详情" width="700px">
      <el-form v-if="detailForm" label-position="top">
        <el-form-item label="公司名称">
          <el-input v-model="detailForm.company_name" size="large" />
        </el-form-item>
        <el-form-item label="职位名称">
          <el-input v-model="detailForm.position_name" size="large" />
        </el-form-item>
        <el-form-item label="JD 原文">
          <el-input v-model="detailForm.jd_text" type="textarea" :rows="8" />
        </el-form-item>

        <el-divider>解析结果</el-divider>

        <el-form-item label="必备技能">
          <div class="tag-edit">
            <el-tag v-for="(skill, idx) in detailForm.parsed_requirements.required_skills" :key="'rs-' + idx" closable round @close="detailForm.parsed_requirements.required_skills.splice(idx, 1)">{{ skill }}</el-tag>
            <el-input v-if="tagInputs.required_skills" ref="requiredSkillInput" v-model="tagValues.required_skills" size="small" class="tag-input" @keyup.enter="addTag('required_skills')" @blur="addTag('required_skills')" />
            <el-button v-else size="small" round @click="tagInputs.required_skills = true">+ 添加</el-button>
          </div>
        </el-form-item>
        <el-form-item label="优选技能">
          <div class="tag-edit">
            <el-tag v-for="(skill, idx) in detailForm.parsed_requirements.preferred_skills" :key="'ps-' + idx" type="success" closable round @close="detailForm.parsed_requirements.preferred_skills.splice(idx, 1)">{{ skill }}</el-tag>
            <el-input v-if="tagInputs.preferred_skills" v-model="tagValues.preferred_skills" size="small" class="tag-input" @keyup.enter="addTag('preferred_skills')" @blur="addTag('preferred_skills')" />
            <el-button v-else size="small" round @click="tagInputs.preferred_skills = true">+ 添加</el-button>
          </div>
        </el-form-item>
        <el-form-item label="经验要求">
          <el-input v-model="detailForm.parsed_requirements.experience_years" style="width: 200px" size="large" />
        </el-form-item>
        <el-form-item label="核心职责">
          <div class="tag-edit">
            <el-tag v-for="(item, idx) in detailForm.parsed_requirements.key_responsibilities" :key="'kr-' + idx" type="warning" closable round @close="detailForm.parsed_requirements.key_responsibilities.splice(idx, 1)">{{ item }}</el-tag>
            <el-input v-if="tagInputs.key_responsibilities" v-model="tagValues.key_responsibilities" size="small" class="tag-input" @keyup.enter="addTag('key_responsibilities')" @blur="addTag('key_responsibilities')" />
            <el-button v-else size="small" round @click="tagInputs.key_responsibilities = true">+ 添加</el-button>
          </div>
        </el-form-item>
        <el-form-item label="技术领域">
          <div class="tag-edit">
            <el-tag v-for="(item, idx) in detailForm.parsed_requirements.technical_domains" :key="'td-' + idx" type="info" closable round @close="detailForm.parsed_requirements.technical_domains.splice(idx, 1)">{{ item }}</el-tag>
            <el-input v-if="tagInputs.technical_domains" v-model="tagValues.technical_domains" size="small" class="tag-input" @keyup.enter="addTag('technical_domains')" @blur="addTag('technical_domains')" />
            <el-button v-else size="small" round @click="tagInputs.technical_domains = true">+ 添加</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDetailDialog = false" round>取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave" round>保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { jobApi } from '@/api'

const jobs = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const form = ref({ company_name: '', position_name: '', jd_text: '' })

const showDetailDialog = ref(false)
const detailForm = ref<any>(null)
const detailJobId = ref('')
const saving = ref(false)

const tagInputs = ref<Record<string, boolean>>({
  required_skills: false,
  preferred_skills: false,
  key_responsibilities: false,
  technical_domains: false,
})
const tagValues = ref<Record<string, string>>({
  required_skills: '',
  preferred_skills: '',
  key_responsibilities: '',
  technical_domains: '',
})

onMounted(() => loadJobs())

async function loadJobs() {
  loading.value = true
  try {
    const res = await jobApi.list()
    jobs.value = res.data.jobs || []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.position_name || !form.value.jd_text) {
    ElMessage.warning('请填写职位名称和 JD')
    return
  }
  creating.value = true
  try {
    await jobApi.create(form.value)
    ElMessage.success('岗位创建成功')
    showCreate.value = false
    form.value = { company_name: '', position_name: '', jd_text: '' }
    await loadJobs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

async function handleSetDefault(id: string) {
  await jobApi.setDefault(id)
  ElMessage.success('已设为默认')
  await loadJobs()
}

async function showDetail(row: any) {
  detailJobId.value = row.id
  const pr = row.parsed_requirements || {}
  detailForm.value = {
    company_name: row.company_name || '',
    position_name: row.position_name || '',
    jd_text: row.jd_text || '',
    parsed_requirements: {
      required_skills: [...(pr.required_skills || [])],
      preferred_skills: [...(pr.preferred_skills || [])],
      experience_years: pr.experience_years || '',
      key_responsibilities: [...(pr.key_responsibilities || [])],
      technical_domains: [...(pr.technical_domains || [])],
    },
  }
  Object.keys(tagInputs.value).forEach(k => { tagInputs.value[k] = false })
  Object.keys(tagValues.value).forEach(k => { tagValues.value[k] = '' })
  showDetailDialog.value = true
}

function addTag(field: string) {
  const val = tagValues.value[field]?.trim()
  if (val && !detailForm.value.parsed_requirements[field].includes(val)) {
    detailForm.value.parsed_requirements[field].push(val)
  }
  tagValues.value[field] = ''
  tagInputs.value[field] = false
}

async function handleSave() {
  saving.value = true
  try {
    await jobApi.update(detailJobId.value, {
      company_name: detailForm.value.company_name,
      position_name: detailForm.value.position_name,
      jd_text: detailForm.value.jd_text,
      parsed_requirements: detailForm.value.parsed_requirements,
    })
    ElMessage.success('保存成功')
    showDetailDialog.value = false
    await loadJobs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确认删除此岗位？', '提示')
  await jobApi.delete(id)
  ElMessage.success('已删除')
  await loadJobs()
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

.item-card__icon--warm {
  background: linear-gradient(135deg, #FFF0EB 0%, #FFE6D9 100%);
  color: #E17055;
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
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.item-card__subtitle {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.item-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
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
  background: linear-gradient(135deg, #FFF0EB 0%, #F0EEFF 100%);
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

/* ── Tag editing ── */
.tag-edit {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.tag-input {
  width: 120px;
}
</style>
