<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="12" :sm="12" :lg="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ '--accent': card.color }">
          <div class="stat-body">
            <div class="stat-info">
              <p class="stat-label">{{ card.label }}</p>
              <p class="stat-value">{{ card.value }}</p>
              <p class="stat-sub">{{ card.sub }}</p>
            </div>
            <div class="stat-icon-wrap">
              <el-icon :size="36"><component :is="card.icon" /></el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <div class="stat-bar" :style="{ width: card.pct + '%' }"></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 提醒卡片 -->
    <el-row :gutter="16" class="alert-row" v-if="stats.expired > 0 || stats.expiring_soon > 0">
      <el-col :span="24">
        <div class="alert-card">
          <div class="alert-item danger" v-if="stats.expired > 0">
            <el-icon><WarningFilled /></el-icon>
            <span><strong>{{ stats.expired }}</strong> 份合同已过期</span>
          </div>
          <div class="alert-item warning" v-if="stats.expiring_soon > 0">
            <el-icon><Bell /></el-icon>
            <span><strong>{{ stats.expiring_soon }}</strong> 份合同将在30天内到期</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 月度趋势 + 状态分布 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="16">
        <div class="card">
          <div class="card-head">
            <h3>月度合同趋势</h3>
            <el-select v-model="selectedYear" style="width:100px" size="small" @change="loadMonthly">
              <el-option v-for="y in [2025, 2026, 2027]" :key="y" :label="y + '年'" :value="y" />
            </el-select>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <div class="y-axis">
                <span v-for="i in 5" :key="i">{{ formatYAxis(maxCount, i) }}</span>
              </div>
              <div class="chart-grid">
                <div v-for="m in monthly" :key="m.month" class="month-col">
                  <div class="bar-area">
                    <div
                      class="bar"
                      :style="{ height: getBarHeight(m.count, maxCount) + '%' }"
                      :title="`${m.month}月: ${m.count}份, ¥${formatMoney(m.amount)}`"
                    >
                      <span class="bar-val" v-if="m.count > 0">{{ m.count }}</span>
                    </div>
                  </div>
                  <span class="month-label">{{ m.month }}月</span>
                </div>
              </div>
            </div>
            <div class="chart-legend">
              <span><i class="dot primary"></i> 合同数量</span>
              <span><i class="dot success"></i> 合同金额</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="8">
        <div class="card">
          <div class="card-head"><h3>合同状态分布</h3></div>
          <div class="card-body">
            <div class="status-list">
              <div v-for="(count, status) in stats.by_status" :key="status" class="status-row">
                <div class="status-info">
                  <span class="status-dot" :class="statusClass(status)"></span>
                  <span class="status-name">{{ status }}</span>
                </div>
                <div class="status-bar-wrap">
                  <div
                    class="status-bar-fill"
                    :class="statusClass(status)"
                    :style="{ width: statusPercent(count) + '%' }"
                  ></div>
                </div>
                <span class="status-count">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 采购员统计 -->
    <el-row :gutter="16">
      <el-col :span="24">
        <div class="card">
          <div class="card-head"><h3>采购员统计</h3></div>
          <div class="card-body">
            <div class="buyer-grid">
              <div v-for="(data, name) in stats.by_buyer" :key="name" class="buyer-card">
                <div class="buyer-header">
                  <span class="buyer-avatar" :style="{ background: buyerColor(name) }">{{ name?.charAt(0) }}</span>
                  <span class="buyer-name">{{ name }}</span>
                </div>
                <div class="buyer-stats">
                  <div class="buyer-stat">
                    <span class="bs-label">合同数</span>
                    <span class="bs-value">{{ data.count }}</span>
                  </div>
                  <div class="buyer-stat">
                    <span class="bs-label">销售金额</span>
                    <span class="bs-value sales">¥{{ formatShort(data.amount) }}</span>
                  </div>
                  <div class="buyer-stat">
                    <span class="bs-label">采购金额</span>
                    <span class="bs-value purchase">¥{{ formatShort(data.purchase_amount) }}</span>
                  </div>
                  <div class="buyer-stat">
                    <span class="bs-label">利润</span>
                    <span class="bs-value" :class="(data.amount - data.purchase_amount) >= 0 ? 'profit-pos' : 'profit-neg'">
                      ¥{{ formatShort(data.amount - data.purchase_amount) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <div class="card quick-card">
      <div class="card-head"><h3>快捷操作</h3></div>
      <div class="card-body">
        <div class="quick-btns">
          <el-button size="large" @click="$router.push('/contracts')">
            <el-icon><Document /></el-icon> 合同管理
          </el-button>
          <el-button size="large" @click="$router.push('/invoices')">
            <el-icon><Tickets /></el-icon> 发票管理
          </el-button>
          <el-button size="large" @click="exportContracts">
            <el-icon><Download /></el-icon> 导出台账
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Document, Tickets, Download, DataAnalysis,
  Money, Folder, Coin, WarningFilled, Bell
} from '@element-plus/icons-vue'
import api from '../api'

const stats = ref({
  total_contracts: 0, total_invoices: 0,
  total_amount: 0, total_purchase: 0,
  total_invoice_amount: 0, total_profit: 0,
  by_status: {}, by_buyer: {}, by_type: {},
  expiring_soon: 0, expired: 0,
})

const selectedYear = ref(new Date().getFullYear())
const monthly = ref(Array.from({ length: 12 }, (_, i) => ({ month: i + 1, count: 0, amount: 0 })))

const maxCount = computed(() => Math.max(...monthly.value.map(m => m.count), 1))

const formatMoney = (v) => (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
const formatShort = (v) => {
  if (!v) return '0'
  if (v >= 10000) return (v / 10000).toFixed(1) + '万'
  return Number(v).toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}
const formatYAxis = (max, i) => Math.round(max * (6 - i) / 5)
const getBarHeight = (val, max) => max > 0 ? Math.max((val / max) * 100, val > 0 ? 8 : 0) : 0
const statusPercent = (count) => {
  const total = Object.values(stats.value.by_status).reduce((a, b) => a + b, 0)
  return total > 0 ? (count / total) * 100 : 0
}

const statusClass = (s) => ({
  '进行中': 'primary', '待开票': 'warning', '待回款': 'info', '已完结': 'success',
}[s] || 'info')

const buyerColors = ['#409EFF', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#b37feb', '#13c2c2', '#eb2f96', '#fa8c16', '#52c41a']
const buyerColorMap = {}
let ci = 0
const buyerColor = (name) => {
  if (!name) return '#c0c4cc'
  if (!buyerColorMap[name]) { buyerColorMap[name] = buyerColors[ci % buyerColors.length]; ci++ }
  return buyerColorMap[name]
}

const totalContracts = computed(() => stats.value.total_contracts)
const statCards = computed(() => [
  { label: '合同总数', value: stats.value.total_contracts, sub: '份', icon: Folder, color: '#409EFF', pct: 100 },
  { label: '合同总额', value: '¥' + formatShort(stats.value.total_amount), sub: '', icon: Money, color: '#67c23a', pct: 80 },
  { label: '发票总额', value: '¥' + formatShort(stats.value.total_invoice_amount), sub: '', icon: Coin, color: '#e6a23c', pct: 60 },
  { label: '总利润', value: '¥' + formatShort(stats.value.total_profit), sub: '', icon: DataAnalysis, color: stats.value.total_profit >= 0 ? '#67c23a' : '#f56c6c', pct: 70 },
])

const loadStats = async () => {
  try {
    const { data } = await api.get('/stats')
    stats.value = data
  } catch (e) { console.error(e) }
}

const loadMonthly = async () => {
  try {
    const { data } = await api.get('/contracts/stats/monthly', { params: { year: selectedYear.value } })
    monthly.value = data
  } catch (e) { console.error(e) }
}

const exportContracts = () => window.open('/api/export/contracts', '_blank')

onMounted(() => {
  loadStats()
  loadMonthly()
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-cards { margin-bottom: 16px; }
.stat-card {
  background: #fff;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: transform 0.25s, box-shadow 0.25s;
  cursor: default;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.stat-body {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.3;
}
.stat-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}
.stat-icon-wrap {
  color: var(--accent);
  opacity: 0.15;
}
.stat-footer {
  height: 3px;
  background: #f5f7fa;
}
.stat-bar {
  height: 100%;
  background: var(--accent);
  transition: width 0.8s ease;
}

.alert-row { margin-bottom: 16px; }
.alert-card {
  background: #fff;
  border-radius: var(--border-radius);
  padding: 14px 20px;
  box-shadow: var(--card-shadow);
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  padding: 6px 14px;
  border-radius: 8px;
}
.alert-item.danger {
  color: #f56c6c;
  background: #fef0f0;
}
.alert-item.warning {
  color: #e6a23c;
  background: #fdf6ec;
}

.chart-row { margin-bottom: 16px; }
.card {
  background: #fff;
  border-radius: var(--border-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
  margin-bottom: 16px;
}
.card-head {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-head h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.card-body { padding: 20px; }

/* 月度图表 */
.chart-container {
  display: flex;
  height: 240px;
  gap: 8px;
}
.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 40px;
  text-align: right;
  font-size: 11px;
  color: #c0c4cc;
  padding: 0 4px;
}
.chart-grid {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 4px;
  border-left: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 4px;
}
.month-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bar-area {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.bar {
  width: 70%;
  max-width: 32px;
  background: linear-gradient(180deg, #409EFF, #66b1ff);
  border-radius: 4px 4px 0 0;
  transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  cursor: pointer;
}
.bar:hover {
  filter: brightness(1.1);
}
.bar-val {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-regular);
}
.month-label {
  margin-top: 8px;
  font-size: 11px;
  color: #c0c4cc;
}
.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  margin-right: 4px;
}
.dot.primary { background: #409EFF; }
.dot.success { background: #67c23a; }

/* 状态分布 */
.status-list { display: flex; flex-direction: column; gap: 14px; }
.status-row { display: flex; align-items: center; gap: 12px; }
.status-info { display: flex; align-items: center; gap: 8px; width: 80px; }
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot.primary { background: #409EFF; }
.status-dot.warning { background: #e6a23c; }
.status-dot.info { background: #909399; }
.status-dot.success { background: #67c23a; }
.status-name { font-size: 13px; color: var(--text-regular); }
.status-bar-wrap {
  flex: 1;
  height: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}
.status-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}
.status-bar-fill.primary { background: #409EFF; }
.status-bar-fill.warning { background: #e6a23c; }
.status-bar-fill.info { background: #909399; }
.status-bar-fill.success { background: #67c23a; }
.status-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  width: 30px;
  text-align: right;
}

/* 采购员统计 */
.buyer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.buyer-card {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 16px;
  transition: box-shadow 0.2s;
}
.buyer-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.buyer-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.buyer-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}
.buyer-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.buyer-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.buyer-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bs-label { font-size: 11px; color: var(--text-secondary); }
.bs-value { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.bs-value.sales { color: #67c23a; }
.bs-value.purchase { color: #e6a23c; }
.profit-pos { color: #67c23a !important; }
.profit-neg { color: #f56c6c !important; }

/* 快捷操作 */
.quick-card { margin-bottom: 0; }
.quick-btns {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.quick-btns .el-button {
  flex: 1;
  min-width: 140px;
  height: 48px;
  border-radius: 10px;
  font-weight: 500;
}
</style>
