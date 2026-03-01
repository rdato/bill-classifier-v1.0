<template>
  <div class="home-page">
    <!-- 上传区域 -->
    <div class="upload-section">
      <div
        class="upload-card"
        :class="{ active: isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="triggerUpload"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls,.csv"
          style="display: none"
          @change="handleFileSelect"
        />
        <div class="upload-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <p class="upload-title">点击或拖拽上传账单文件</p>
        <p class="upload-hint">支持支付宝、微信、银行账单 (xlsx/xls/csv)</p>
      </div>

      <div class="action-buttons" v-if="stats.total_records > 0">
        <button class="btn btn-primary" @click="handleExport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出
        </button>
        <button class="btn btn-ghost" @click="handleClear">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          清空
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="uploading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在处理...</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-grid" v-if="stats.total_records > 0">
      <div class="stat-card">
        <div class="stat-icon expense">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <polyline points="19 12 12 19 5 12"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">总支出</span>
          <span class="stat-value">¥{{ formatMoney(stats.total_expense) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon income">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="19" x2="12" y2="5"/>
            <polyline points="5 12 12 5 19 12"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">总收入</span>
          <span class="stat-value">¥{{ formatMoney(stats.total_income) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon neutral">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">净支出</span>
          <span class="stat-value">¥{{ formatMoney(stats.net_expense) }}</span>
        </div>
      </div>
    </div>

    <!-- 分类汇总 -->
    <div class="section" v-if="categorySummary.length > 0">
      <div class="section-header">
        <h2>分类汇总</h2>
        <span class="badge">{{ categorySummary.length }} 个类别</span>
      </div>

      <div class="category-list">
        <div
          v-for="(item, index) in categorySummary"
          :key="item.category"
          class="category-item"
        >
          <div class="category-main">
            <div class="category-info">
              <span class="category-dot" :style="{ background: colors[index % colors.length] }"></span>
              <span class="category-name">{{ item.category }}</span>
            </div>
            <div class="category-meta">
              <span class="category-amount">¥{{ formatMoney(item.expense) }}</span>
              <span class="category-count">{{ item.expense_count }}笔</span>
            </div>
          </div>
          <div class="category-bar">
            <div
              class="category-bar-fill"
              :style="{
                width: item.percentage + '%',
                background: colors[index % colors.length]
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 交易明细 -->
    <div class="section" v-if="records.length > 0">
      <div class="section-header">
        <h2>交易明细</h2>
        <div class="filters">
          <select v-model="filters.category" @change="loadRecords" class="select">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <select v-model="filters.type" @change="loadRecords" class="select">
            <option value="">全部类型</option>
            <option value="支出">支出</option>
            <option value="收入">收入</option>
          </select>
          <select v-model="filters.source" @change="loadRecords" class="select">
            <option value="">全部来源</option>
            <option value="支付宝">支付宝</option>
            <option value="微信">微信</option>
            <option value="银行">银行</option>
          </select>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>日期</th>
              <th>分类</th>
              <th>交易对方</th>
              <th>描述</th>
              <th class="right">金额</th>
              <th>来源</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="record.id">
              <td class="date">{{ formatDate(record.date) }}</td>
              <td>
                <select
                  v-model="record.category"
                  class="inline-select"
                  @change="handleCategoryChange(record)"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </td>
              <td class="ellipsis">{{ record.merchant || '-' }}</td>
              <td class="ellipsis">{{ record.description || '-' }}</td>
              <td class="right" :class="record.type === '收入' ? 'income' : 'expense'">
                {{ record.type === '收入' ? '+' : '-' }}¥{{ formatMoney(record.amount) }}
              </td>
              <td>
                <span class="source-tag" :class="getSourceClass(record.source)">
                  {{ record.source }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button
          class="page-btn"
          :disabled="pagination.page === 1"
          @click="pagination.page--; loadRecords()"
        >
          上一页
        </button>
        <span class="page-info">
          {{ pagination.page }} / {{ totalPages }}
        </span>
        <button
          class="page-btn"
          :disabled="pagination.page >= totalPages"
          @click="pagination.page++; loadRecords()"
        >
          下一页
        </button>
        <span class="total">共 {{ pagination.total }} 条</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="stats.total_records === 0 && !uploading" class="empty">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="12" y1="18" x2="12" y2="12"/>
          <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
      </div>
      <h3>暂无数据</h3>
      <p>上传账单文件开始使用</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// API
const api = axios.create({ baseURL: '/api', timeout: 60000 })
api.interceptors.response.use(
  res => res.data,
  err => Promise.reject(new Error(err.response?.data?.error || err.message || '请求失败'))
)

const uploadFileApi = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}
const getRecords = (params) => api.get('/records', { params })
const updateRecord = (id, data) => api.put(`/records/${id}`, data)
const getStats = () => api.get('/stats')
const exportExcelApi = () => api.get('/export', { responseType: 'blob' })
const clearRecordsApi = () => api.post('/clear')

const props = defineProps({ stats: Object, categories: Array })
const emit = defineEmits(['refresh'])

const colors = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316',
  '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#06b6d4',
  '#0ea5e9', '#3b82f6'
]

const uploading = ref(false)
const isDragOver = ref(false)
const records = ref([])
const fileInput = ref(null)

const filters = ref({ category: '', type: '', source: '' })
const pagination = ref({ page: 1, per_page: 20, total: 0 })

const formatMoney = (v) => v?.toFixed(2)?.replace(/\B(?=(\d{3})+(?!\d))/g, ',') || '0.00'
const formatDate = (d) => d?.replace(/(\d{4})-(\d{2})-(\d{2}).*/, '$1/$2/$3') || d
const getSourceClass = (s) => ({ '支付宝': 'alipay', '微信': 'wechat', '银行': 'bank' }[s] || '')

const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.per_page) || 1)

const categorySummary = computed(() => {
  const cats = props.stats.categories || {}
  const total = props.stats.total_expense || 0
  return Object.entries(cats)
    .map(([category, data]) => ({
      category,
      expense: data.expense || 0,
      expense_count: data.expense_count || 0,
      percentage: total ? ((data.expense || 0) / total) * 100 : 0
    }))
    .filter(i => i.expense > 0)
    .sort((a, b) => b.expense - a.expense)
})

const triggerUpload = () => fileInput.value?.click()

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) processFile(file)
}

const processFile = async (file) => {
  uploading.value = true
  try {
    const result = await uploadFileApi(file)
    ElMessage.success(`上传成功，解析了 ${result.record_count} 条记录`)
    emit('refresh')
    loadRecords()
  } catch (err) {
    ElMessage.error(err.message || '上传失败')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const loadRecords = async () => {
  try {
    const result = await getRecords({ page: pagination.value.page, per_page: pagination.value.per_page, ...filters.value })
    records.value = result.records
    pagination.value.total = result.total
  } catch (err) {
    ElMessage.error('加载失败')
  }
}

const handleCategoryChange = async (row) => {
  try {
    await updateRecord(row.id, { category: row.category })
    ElMessage.success('已更新')
    emit('refresh')
  } catch (err) {
    ElMessage.error('更新失败')
  }
}

const handleExport = async () => {
  try {
    const res = await exportExcelApi()
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `账单分类_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (err) {
    ElMessage.error('导出失败')
  }
}

const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定清空所有数据？此操作不可恢复。', '提示', { type: 'warning' })
    await clearRecordsApi()
    records.value = []
    emit('refresh')
    ElMessage.success('已清空')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清空失败')
  }
}

onMounted(() => { if (props.stats.total_records > 0) loadRecords() })
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 上传区域 */
.upload-section {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.upload-card {
  flex: 1;
  background: #fff;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-card:hover,
.upload-card.active {
  border-color: #6366f1;
  background: #faf5ff;
}

.upload-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: #6366f1;
}

.upload-icon svg {
  width: 100%;
  height: 100%;
}

.upload-title {
  font-size: 15px;
  color: #334155;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 13px;
  color: #94a3b8;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: #6366f1;
  color: #fff;
}

.btn-primary:hover {
  background: #4f46e5;
}

.btn-ghost {
  background: #fff;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-ghost:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

/* 加载 */
.loading-overlay {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-icon.expense {
  background: #fef2f2;
  color: #ef4444;
}

.stat-icon.income {
  background: #ecfdf5;
  color: #10b981;
}

.stat-icon.neutral {
  background: #f1f5f9;
  color: #64748b;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  font-variant-numeric: tabular-nums;
}

/* 通用区块 */
.section {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.badge {
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 12px;
}

/* 分类列表 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.category-name {
  font-size: 14px;
  color: #334155;
}

.category-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-amount {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  font-variant-numeric: tabular-nums;
}

.category-count {
  font-size: 12px;
  color: #94a3b8;
}

.category-bar {
  height: 4px;
  background: #f1f5f9;
  border-radius: 2px;
  overflow: hidden;
}

.category-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

/* 筛选 */
.filters {
  display: flex;
  gap: 8px;
}

.select {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  color: #475569;
  background: #fff;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: #6366f1;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  padding: 12px;
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
  border-bottom: 1px solid #e2e8f0;
}

.table th.right { text-align: right; }

.table td {
  padding: 14px 12px;
  font-size: 13px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.table .date {
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.table .ellipsis {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table .right {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
}

.table .income { color: #10b981; }
.table .expense { color: #ef4444; }

.inline-select {
  padding: 4px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 13px;
  color: #334155;
  background: #fff;
  cursor: pointer;
}

.source-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.source-tag.alipay {
  background: #eff6ff;
  color: #3b82f6;
}

.source-tag.wechat {
  background: #ecfdf5;
  color: #10b981;
}

.source-tag.bank {
  background: #fffbeb;
  color: #d97706;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
  color: #475569;
  font-size: 13px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f8fafc;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #334155;
}

.total {
  font-size: 12px;
  color: #94a3b8;
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #cbd5e1;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty h3 {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 4px;
}

.empty p {
  font-size: 14px;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .upload-section {
    flex-direction: column;
  }

  .action-buttons {
    flex-direction: row;
    width: 100%;
  }

  .action-buttons .btn {
    flex: 1;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    flex-wrap: wrap;
  }
}
</style>
