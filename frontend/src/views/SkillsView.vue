<template>
  <div v-loading="loading">
    <div class="page__toolbar">
      <div class="page__count">
        <span class="page__count-num">{{ categories.length }}</span> 个技能类别
      </div>
      <div class="toolbar__actions">
        <el-select v-model="selectedResumeId" placeholder="选择简历" style="width: 200px;" :disabled="!resumes.length">
          <el-option v-for="r in resumes" :key="r.id" :label="r.title || '未命名简历'" :value="r.id" />
        </el-select>
        <el-button type="primary" round @click="handleRebuild" :loading="rebuilding" :disabled="!selectedResumeId">
          重建技能树
        </el-button>
      </div>
    </div>

    <el-empty v-if="!skills.length && !loading" description="暂无技能数据，上传简历后自动生成" />

    <template v-if="skills.length">
      <!-- Radar Chart + Advice -->
      <el-card class="radar-card">
        <template #header>技能雷达图</template>
        <div class="radar-layout">
          <v-chart class="radar-chart" :option="radarOption" autoresize />
          <div class="advice-panel">
            <div class="advice-block">
              <div class="advice-title strength-title">主打领域建议</div>
              <div class="advice-content">{{ strengthAdvice || '暂无建议，请先重建技能树' }}</div>
            </div>
            <div class="advice-block">
              <div class="advice-title weakness-title">弱项提升建议</div>
              <div class="advice-content">{{ weaknessAdvice || '暂无建议，请先重建技能树' }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Infinite Carousel -->
      <div class="carousel-section" v-if="categories.length">
        <div class="carousel-header">
          <span class="carousel-title">技能分类</span>
          <span class="carousel-indicator" v-if="categories.length > VISIBLE">{{ displayIndex + 1 }} / {{ categories.length }}</span>
        </div>
        <div class="carousel-wrapper">
          <button v-if="categories.length > VISIBLE" class="carousel-arrow" @click="scrollPrev">
            <el-icon><ArrowLeft /></el-icon>
          </button>

          <div class="carousel-viewport">
            <div
              ref="trackRef"
              class="carousel-track"
              :class="{ 'no-transition': skipTransition }"
              :style="trackStyle"
              @transitionend="onTransitionEnd"
            >
              <div
                v-for="(cat, i) in displayList"
                :key="`card-${i}`"
                class="carousel-card-slot"
                :style="{ width: cardWidth }"
              >
                <div class="carousel-card-inner">
                  <el-card class="category-card" shadow="hover">
                    <template #header>
                      <div class="category-header">
                        <span>{{ translateCategory(cat.name) }}</span>
                        <el-tag size="small" type="info">平均 {{ cat.avg.toFixed(1) }}</el-tag>
                      </div>
                    </template>
                    <div v-for="skill in cat.children" :key="skill.id" class="skill-item">
                      <el-tooltip :content="skill.evaluation_comment || '暂无评价'" placement="top" :disabled="!skill.evaluation_comment">
                        <div class="skill-row">
                          <span class="skill-name">{{ skill.skill_name }}</span>
                          <el-progress
                            :percentage="skill.proficiency_score * 10"
                            :stroke-width="14"
                            :color="scoreColor(skill.proficiency_score)"
                            :format="() => `${skill.proficiency_score}`"
                            style="flex: 1; margin-left: 12px;"
                          />
                          <el-tag v-if="skill.source_type === 'inferred_gap'" type="danger" size="small" class="source-tag">Gap</el-tag>
                        </div>
                      </el-tooltip>
                    </div>
                    <div v-if="!cat.children.length" class="empty-cat">无技能</div>
                  </el-card>
                </div>
              </div>
            </div>
          </div>

          <button v-if="categories.length > VISIBLE" class="carousel-arrow" @click="scrollNext">
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>

        <!-- Dot indicators -->
        <div class="carousel-dots" v-if="categories.length > VISIBLE">
          <span
            v-for="i in categories.length" :key="i"
            class="carousel-dot"
            :class="{ active: (i - 1) === displayIndex }"
          />
        </div>
      </div>

      <!-- Orphan skills -->
      <el-card v-if="orphanSkills.length" class="category-card orphan-card">
        <template #header>
          <div class="category-header"><span>其他技能</span></div>
        </template>
        <div v-for="skill in orphanSkills" :key="skill.id" class="skill-item">
          <el-tooltip :content="skill.evaluation_comment || '暂无评价'" placement="top" :disabled="!skill.evaluation_comment">
            <div class="skill-row">
              <span class="skill-name">{{ skill.skill_name }}</span>
              <el-progress
                :percentage="skill.proficiency_score * 10"
                :stroke-width="14"
                :color="scoreColor(skill.proficiency_score)"
                :format="() => `${skill.proficiency_score}`"
                style="flex: 1; margin-left: 12px;"
              />
            </div>
          </el-tooltip>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { skillApi, resumeApi } from '@/api'

use([RadarChart, TooltipComponent, LegendComponent, CanvasRenderer])

/** 可视区域同时展示的卡片数 */
const VISIBLE = 3

const categoryNameMap: Record<string, string> = {
  languages: '编程语言',
  frameworks: '框架',
  databases: '数据库',
  tools: '工具',
  domains: '领域知识',
  middleware: '中间件',
  frontend_frameworks: '前端框架',
  backend_frameworks: '后端框架',
  etl_tools: 'ETL 工具',
  visualization: '可视化',
  devops: '运维/DevOps',
  cloud: '云服务',
  testing: '测试',
  ai_frameworks: 'AI 框架',
  ai_tools: 'AI 工具',
  data_tools: '数据工具',
  frontend: '前端',
  backend: '后端',
  mobile: '移动端',
  os: '操作系统',
  big_data: '大数据',
  security: '安全',
  network: '网络',
  other: '其他',
}

function translateCategory(name: string): string {
  const lower = name.toLowerCase().replace(/[\s-]/g, '_')
  const cn = categoryNameMap[lower] || categoryNameMap[name]
  if (cn) return `${cn} ${name}`
  return name
}

const skills = ref<any[]>([])
const resumes = ref<any[]>([])
const loading = ref(false)
const rebuilding = ref(false)
const selectedResumeId = ref('')
const strengthAdvice = ref('')
const weaknessAdvice = ref('')

// ---- Infinite carousel state ----
const trackRef = ref<HTMLElement>()
const innerOffset = ref(0)
const skipTransition = ref(false)

/**
 * 无限轮播核心：
 *   displayList = [clone_last_V, ...real, clone_first_V]
 *   innerOffset 初始 = V，指向第一张真实卡片
 *   滚到克隆区后，瞬间跳回对应真实位置
 */
const displayList = computed(() => {
  const cats = categories.value
  if (cats.length <= VISIBLE) return cats
  return [...cats.slice(-VISIBLE), ...cats, ...cats.slice(0, VISIBLE)]
})

const cardWidth = computed(() => `${100 / VISIBLE}%`)

const trackStyle = computed(() => ({
  transform: `translateX(-${innerOffset.value * (100 / VISIBLE)}%)`,
}))

// 当前逻辑索引（0-based，对应 categories 的下标）
const displayIndex = computed(() => {
  const n = categories.value.length
  if (n <= VISIBLE) return 0
  return ((innerOffset.value - VISIBLE) % n + n) % n
})

function scrollNext() {
  if (categories.value.length <= VISIBLE) return
  innerOffset.value++
}

function scrollPrev() {
  if (categories.value.length <= VISIBLE) return
  innerOffset.value--
}

function onTransitionEnd(e: TransitionEvent) {
  if (e.target !== trackRef.value) return
  const n = categories.value.length
  if (n <= VISIBLE) return

  if (innerOffset.value >= VISIBLE + n) {
    snapTo(innerOffset.value - n)
  } else if (innerOffset.value < VISIBLE) {
    snapTo(innerOffset.value + n)
  }
}

function snapTo(newOffset: number) {
  skipTransition.value = true
  innerOffset.value = newOffset
  nextTick(() => {
    void trackRef.value?.offsetHeight   // force reflow
    skipTransition.value = false
  })
}

// ---- Data & computed ----
onMounted(async () => {
  loading.value = true
  try {
    const [skillRes, resumeRes] = await Promise.all([
      skillApi.getTree(),
      resumeApi.list(),
    ])
    skills.value = skillRes.data.skills || []
    strengthAdvice.value = skillRes.data.strength_advice || ''
    weaknessAdvice.value = skillRes.data.weakness_advice || ''
    const allResumes = resumeRes.data.resumes || []
    resumes.value = allResumes.filter((r: any) => r.parsing_status === 'completed')
    if (resumes.value.length) {
      selectedResumeId.value = resumes.value[0].id
    }
  } catch { /* empty */ }
  finally {
    loading.value = false
  }
})

const rootSkills = computed(() => skills.value.filter((s: any) => !s.parent_skill_id))

const categories = computed(() => {
  const rootIds = new Set(rootSkills.value.map((s: any) => s.id))
  const childMap = new Map<string, any[]>()

  for (const s of skills.value) {
    if (s.parent_skill_id && rootIds.has(s.parent_skill_id)) {
      if (!childMap.has(s.parent_skill_id)) childMap.set(s.parent_skill_id, [])
      childMap.get(s.parent_skill_id)!.push(s)
    }
  }

  return rootSkills.value
    .filter((r: any) => childMap.has(r.id))
    .map((r: any) => {
      const children = childMap.get(r.id) || []
      const scores = children.map((c: any) => c.proficiency_score)
      const avg = scores.length ? scores.reduce((a: number, b: number) => a + b, 0) / scores.length : 0
      return { name: r.skill_name, id: r.id, children, avg }
    })
})

// 当 categories 变化（首次加载 / 重建）时重置偏移
watch(categories, (cats) => {
  skipTransition.value = true
  innerOffset.value = cats.length > VISIBLE ? VISIBLE : 0
  nextTick(() => {
    void trackRef.value?.offsetHeight
    skipTransition.value = false
  })
})

const orphanSkills = computed(() => {
  const categoryIds = new Set(categories.value.map((c: any) => c.id))
  const parentIds = new Set(skills.value.map((s: any) => s.parent_skill_id).filter(Boolean))
  return rootSkills.value.filter((s: any) => !categoryIds.has(s.id) && !parentIds.has(s.id))
})

const radarOption = computed(() => {
  const cats = categories.value
  if (!cats.length) return {}

  return {
    tooltip: {},
    radar: {
      indicator: cats.map((c: any) => ({ name: translateCategory(c.name), max: 10 })),
      shape: 'polygon',
      radius: '65%',
    },
    series: [{
      type: 'radar',
      data: [{
        value: cats.map((c: any) => parseFloat(c.avg.toFixed(1))),
        name: '技能评分',
        areaStyle: { opacity: 0.3 },
        lineStyle: { width: 2 },
      }],
    }],
  }
})

function scoreColor(score: number) {
  if (score >= 7) return '#00B894'
  if (score >= 4) return '#FDCB6E'
  return '#FF6B6B'
}

async function handleRebuild() {
  if (!selectedResumeId.value) return
  try {
    await ElMessageBox.confirm('重建将清空当前所有技能数据并重新生成，确认继续？', '重建技能树')
  } catch { return }

  rebuilding.value = true
  try {
    const res = await skillApi.rebuild(selectedResumeId.value)
    skills.value = res.data.skills || []
    strengthAdvice.value = res.data.strength_advice || ''
    weaknessAdvice.value = res.data.weakness_advice || ''
    ElMessage.success('技能树重建完成')
  } catch (e: any) {
    const msg = e.response?.data?.detail || (e.code === 'ECONNABORTED' ? '请求超时，请稍后重试' : '重建失败，请检查网络连接')
    ElMessage.error(msg)
  } finally {
    rebuilding.value = false
  }
}
</script>

<style scoped>
/* ── Page toolbar ── */
.page__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.page__count { font-size: 14px; color: var(--color-text-muted); }
.page__count-num { font-size: 20px; font-weight: 800; color: var(--color-text); margin-right: 4px; }
.toolbar__actions { display: flex; align-items: center; gap: 12px; }

/* ── Radar card ── */
.radar-card { margin-bottom: 24px; border-radius: var(--radius-lg); }
.radar-layout { display: flex; gap: 20px; align-items: stretch; }
.radar-chart { flex: 3; height: 350px; min-width: 0; }
.advice-panel { flex: 2; display: flex; flex-direction: column; gap: 16px; justify-content: center; }
.advice-block {
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  padding: 16px;
}
.advice-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; }
.strength-title { color: var(--color-secondary); }
.weakness-title { color: #FDCB6E; }
.advice-content { font-size: 14px; color: var(--color-text-secondary); line-height: 1.6; }

/* ── Infinite Carousel ── */
.carousel-section { margin-bottom: 20px; }
.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.carousel-title { font-size: 16px; font-weight: 700; color: var(--color-text); }
.carousel-indicator { font-size: 13px; color: var(--color-text-muted); }

.carousel-wrapper { display: flex; align-items: stretch; gap: 8px; }

.carousel-arrow {
  flex-shrink: 0;
  width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 18px;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}
.carousel-arrow:hover {
  background: var(--color-primary-bg, #F0EEFF);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.carousel-viewport { flex: 1; overflow: hidden; }

.carousel-track {
  display: flex;
  transition: transform 0.4s ease;
}
.carousel-track.no-transition {
  transition: none !important;
}

.carousel-card-slot {
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 0 8px;
}

.carousel-card-inner { height: 100%; }
.category-card { height: 100%; }
.category-header { display: flex; justify-content: space-between; align-items: center; }

.skill-item { margin-bottom: 10px; }
.skill-item:last-child { margin-bottom: 0; }
.skill-row { display: flex; align-items: center; }
.skill-name {
  min-width: 80px;
  font-size: 14px;
  white-space: nowrap;
  color: var(--color-text-secondary);
}
.source-tag { margin-left: 8px; }
.empty-cat {
  color: var(--color-text-muted);
  text-align: center;
  padding: 20px;
  font-size: 13px;
}

/* ── Dots ── */
.carousel-dots { display: flex; justify-content: center; gap: 6px; margin-top: 14px; }
.carousel-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
}
.carousel-dot.active {
  background: var(--color-primary);
  transform: scale(1.3);
}

.orphan-card { margin-top: 4px; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .radar-layout {
    flex-direction: column;
  }
  .radar-chart {
    height: 280px;
  }
}
</style>
