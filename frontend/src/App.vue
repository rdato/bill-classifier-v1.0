<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 顶部导航 -->
      <header class="app-header">
        <div class="header-inner">
          <div class="logo">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M2 10h20"/>
                <path d="M12 4v16"/>
              </svg>
            </div>
            <div class="logo-text">
              <h1>账单分类</h1>
              <p>智能记账助手</p>
            </div>
          </div>

          <div class="header-stats" v-if="stats.total_records > 0">
            <div class="stat-item">
              <span class="stat-label">支出</span>
              <span class="stat-value expense">¥{{ formatMoney(stats.total_expense) }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-label">收入</span>
              <span class="stat-value income">¥{{ formatMoney(stats.total_income) }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-label">记录</span>
              <span class="stat-value">{{ stats.total_records }}笔</span>
            </div>
          </div>
        </div>
      </header>

      <!-- 主内容 -->
      <main class="app-main">
        <router-view
          :stats="stats"
          :categories="categories"
          @refresh="loadData"
        />
      </main>

      <!-- 底部 -->
      <footer class="app-footer">
        <p>数据仅存储在本地，安全可靠</p>
      </footer>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { getStats, getCategories } from './api/bill'

const stats = ref({
  total_expense: 0,
  total_income: 0,
  total_records: 0
})
const categories = ref([])

const formatMoney = (value) => {
  return value?.toFixed(2)?.replace(/\B(?=(\d{3})+(?!\d))/g, ',') || '0.00'
}

const loadData = async () => {
  try {
    const [statsRes, catRes] = await Promise.all([getStats(), getCategories()])
    stats.value = statsRes
    categories.value = catRes.categories
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  background: #f8fafc;
  color: #334155;
  min-height: 100vh;
  line-height: 1.6;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.app-header {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-icon svg {
  width: 22px;
  height: 22px;
}

.logo-text h1 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.logo-text p {
  font-size: 12px;
  color: #94a3b8;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-item {
  text-align: right;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
  font-variant-numeric: tabular-nums;
}

.stat-value.expense { color: #ef4444; }
.stat-value.income { color: #10b981; }

.stat-divider {
  width: 1px;
  height: 32px;
  background: #e2e8f0;
}

/* 主内容 */
.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

/* 底部 */
.app-footer {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
  font-size: 13px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

/* 全局卡片样式 */
.card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Element Plus 覆盖 */
.el-card {
  background: #fff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 16px !important;
  box-shadow: none !important;
}

.el-button--primary {
  background: #6366f1 !important;
  border-color: #6366f1 !important;
}

.el-button--primary:hover {
  background: #4f46e5 !important;
  border-color: #4f46e5 !important;
}

.el-tag--danger {
  background: #fef2f2 !important;
  border-color: #fecaca !important;
  color: #ef4444 !important;
}

.el-tag--success {
  background: #ecfdf5 !important;
  border-color: #a7f3d0 !important;
  color: #10b981 !important;
}
</style>
