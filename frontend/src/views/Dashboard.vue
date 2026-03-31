<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="item in statCards" :key="item.label">
        <div class="stat-card" :style="{ '--accent': item.color }">
          <div class="stat-card-body">
            <div class="stat-info">
              <span class="stat-label">{{ item.label }}</span>
              <span class="stat-value">{{ item.value }}</span>
              <span class="stat-sub">{{ item.sub }}</span>
            </div>
            <div class="stat-icon">
              <el-icon :size="40"><component :is="item.icon" /></el-icon>
            </div>
          </div>
          <div class="stat-card-footer">
            <div class="stat-bar" :style="{ width: item.percent + '%' }"></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 月度统计 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <div class="card">
          <div class="card-header">
            <h3>月度合同统计</h3>
            <div class="card-header-right">
              <el-select v-model="selectedYear" style="width:100px" @change="loadMonthlyData">
                <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
              </el-select>
            </div>
          </div>
          <div class="card-body">
            <div class="monthly-chart">
              <div v-for="(m, idx) in monthlyData" :key="idx" class="month-bar-group">
                <div class="month-bars">
                  <div class="bar-wrapper">
                    <div class="bar count-bar" :style="{ height: getBarHeight(m.count, maxCount) + '%' }">
                      <span class="bar-value" v-if="m.count > 0">{{ m.count }}</span>
                    </div>
                  </div>
                  <div class="bar-wrapper">
                    <div class="bar amount-bar" :style="{ height: getBarHeight(m.amount, maxAmount) + '%' }">
                      <span class="bar-value" v-if="m.amount > 0">{{ formatShort(m.amount) }}</span>
                    </div>
                  </div>
                </div>
                <span class="month-label">{{ m.month }}月</span>
              </div>
            </div>
            <div class="chart-legend">
              <span class="legend-item"><span class="legend-dot count-dot"></span> 合同数量</span>
              <span class="legend-item"><span class="legend-dot amount-dot"></span> 合同金额</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 合同状态 + 采购员 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-header"><h3>合同状态分布</h3></div>
          <div class="card-body">
            <div class="status-chart">
              <div v-for="(val, key) in stats.by_status" :key="key" class="status-ring">
                <div class="ring" :class="statusClass(key)" :style="{ '--pct': getStatusPercent(val) }">
                  <span class="ring-value">{{ val }}</span>
                </div>
                <span class="ring-label">{{ key }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-header"><h3>采购员统计</h3></div>
          <div class="card-body">
            <div class="buyer-chart">
              <div v-for="(val, key) in stats.by_buyer" :key="key" class="buyer-bar-row">
                <span class="buyer-name">{{ key }}</span>
                <div class="buyer-bar-track">
                  <div class="buyer-bar-fill" :style="{ width: getBarWidth(val.amount) + '%', background: buyerColor(key) }">
                    <span class="buyer-bar-label">{{ val.count }}份 ¥{{ formatShort(val.amount) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <div class="card">
      <div class="card-header"><h3>快速操作</h3></div>
      <div class="card-body">
        <div class="quick-actions">
          <el-button type="primary" size="large" @click="$router.push('/contracts')">
            <el-icon><Document /></el-icon> 查看合同
          </el-button>
          <el-button type="success" size="large" @click="$router.push('/invoices')">
            <el-icon><Tickets /></el-icon> 查看发票
          </el-button>
          <el-button type="warning" size="large" @click="exportContracts">
            <el-icon><Download /></el-icon> 导出台账
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Document, Tickets, Download, DataAnalysis, Money, Folder, Coin } from '@element-plus/icons-vue'
import api from '../api'

const stats = ref({
  total_contracts: 0, total_invoices: 0,
  total_amount: 0, total_invoice_amount: 0,
  total_sales: 0, total_purchase: 0, total_items: 0,
  by_status: {}, by_buyer: {}
})

const selectedYear = ref(new Date().getFullYear())
const years = [2025, 2026]
const monthlyData = ref([])

// 采购员颜色自动生成
const buyerColorPalette = [
  '#409EFF', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#b37feb',
  '#13c2c2', '#eb2f96', '#fa8c16', '#52c41a', '#722ed1', '#2f54eb'
]
const buyerColorMap = {}
let colorIdx = 0
const buyerColor = (name) => {
  if (!name) return '#c0c4cc'
  if (!buyerColorMap[name]) {
    buyerColorMap[name] = buyerColorPalette[colorIdx % buyerColorPalette.length]
    colorIdx++
  }
  return buyerColorMap[name]
}

const maxCount = computed(() => Math.max(...monthlyData.value.map(m => m.count), 1))
const maxAmount = computed(() => Math.max(...monthlyData.value.map(m => m.amount), 1))

const statCards = computed(() => [
  { label: '合同总数', value: stats.value.total_contracts, sub: '份', icon: Folder, color: '#409EFF', percent: 100 },
  { label: '合同总额', value: '¥' + formatMoney(stats.value.total_amount), sub: '', icon: Money, color: '#67c23a', percent: 80 },
  { label: '发票总数', value: stats.value.total_invoices, sub: '份', icon: Tickets, color: '#e6a23c', percent: 70 },
  { label: '发票总额', value: '¥' + formatMoney(stats.value.total_invoice_amount), sub: '', icon: Coin, color: '#f56c6c', percent: 60 }
])

const formatMoney = (v) => (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
const formatShort = (v) => {
  if (!v) return '0'
  if (v >= 10000) return (v / 10000).toFixed(1) + '万'
  return v.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}
const getBarWidth = (amount) => {
  const max = Math.max(...Object.values(stats.value.by_buyer).map(v => v.amount), 1)
  return Math.max((amount / max) * 100, 8)
}
const getBarHeight = (val, max) => Math.max((val / max) * 100, 3)
const getStatusPercent = (val) => {
  const total = Object.values(stats.value.by_status).reduce((a, b) => a + b, 0)
  return total ? Math.round((val / total) * 100) : 0
}
const statusClass = (key) => ({
  '进行中': 'primary', '待开票': 'warning', '待回款': 'info', '已完结': 'success',
  '已开票': 'success', '已交货': 'warning', '未交货': 'info'
}[key] || 'info')
const exportContracts = () => window.open('/api/export/contracts', '_blank')

const loadMonthlyData = async () => {
  try {
    const { data } = await api.get('/contracts', { params: { size: 1000 } })
    const monthly = {}
    for (let m = 1; m <= 12; m++) {
      monthly[m] = { count: 0, amount: 0 }
    }
    data.items.forEach(c => {
      if (c.sign_date) {
        // 解析日期，支持 "2025.1.3" 或 "2025-01-03" 格式
        const parts = c.sign_date.replace(/年|月/g, '.').replace(/日/g, '').split(/[.\-\/]/)
        if (parts.length >= 2) {
          const year = parseInt(parts[0])
          const month = parseInt(parts[1])
          if (year === selectedYear.value && month >= 1 && month <= 12) {
            monthly[month].count++
            monthly[month].amount += (c.amount || 0)
          }
        }
      }
    })
    monthlyData.value = Array.from({ length: 12 }, (_, i) => ({
      month: i + 1,
      count: monthly[i + 1].count,
      amount: monthly[i + 1].amount
    }))
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  const { data } = await api.get('/stats')
  stats.value = data
  await loadMonthlyData()
})
</script>

<style scoped>
.dashboard { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.stat-row { margin-bottom: 20px; }
.stat-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: var(--card-shadow); transition: transform 0.3s, box-shadow 0.3s; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.stat-card-body { padding: 24px; display: flex; justify-content: space-between; align-items: center; }
.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 13px; color: #909399; margin-bottom: 8px; font-weight: 500; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--accent); line-height: 1.2; }
.stat-sub { font-size: 12px; color: #c0c4cc; }
.stat-icon { color: var(--accent); opacity: 0.2; }
.stat-card-footer { height: 3px; background: #f5f7fa; }
.stat-bar { height: 100%; background: var(--accent); border-radius: 0 3px 3px 0; transition: width 1s ease; }

.card { background: #fff; border-radius: 12px; box-shadow: var(--card-shadow); overflow: hidden; }
.card-header { padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { font-size: 15px; font-weight: 600; color: #303133; margin: 0; }
.card-body { padding: 24px; }
.chart-row { margin-bottom: 20px; }

/* 月度柱状图 */
.monthly-chart { display: flex; justify-content: space-between; align-items: flex-end; height: 220px; padding: 0 10px; }
.month-bar-group { display: flex; flex-direction: column; align-items: center; flex: 1; }
.month-bars { display: flex; gap: 3px; align-items: flex-end; height: 180px; width: 100%; justify-content: center; }
.bar-wrapper { width: 20px; height: 100%; display: flex; align-items: flex-end; }
.bar { width: 100%; border-radius: 3px 3px 0 0; transition: height 0.6s ease; position: relative; min-height: 2px; }
.count-bar { background: linear-gradient(180deg, #409EFF, #66b1ff); }
.amount-bar { background: linear-gradient(180deg, #67c23a, #95d475); }
.bar-value { position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 10px; color: #606266; white-space: nowrap; }
.month-label { margin-top: 8px; font-size: 12px; color: #909399; }
.chart-legend { display: flex; justify-content: center; gap: 24px; margin-top: 16px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #606266; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; }
.count-dot { background: #409EFF; }
.amount-dot { background: #67c23a; }

/* 状态图 */
.status-chart { display: flex; justify-content: space-around; }
.status-ring { text-align: center; }
.ring { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; position: relative; }
.ring::before { content: ''; position: absolute; inset: 4px; border-radius: 50%; background: #fff; }
.ring-value { position: relative; z-index: 1; font-size: 22px; font-weight: 700; }
.ring.success { background: conic-gradient(#67c23a calc(var(--pct) * 3.6deg), #e8f5e9 0); }
.ring.warning { background: conic-gradient(#e6a23c calc(var(--pct) * 3.6deg), #fdf6ec 0); }
.ring.info { background: conic-gradient(#909399 calc(var(--pct) * 3.6deg), #f4f4f5 0); }
.ring.primary { background: conic-gradient(#409EFF calc(var(--pct) * 3.6deg), #ecf5ff 0); }
.ring.success .ring-value { color: #67c23a; }
.ring.warning .ring-value { color: #e6a23c; }
.ring.info .ring-value { color: #909399; }
.ring.primary .ring-value { color: #409EFF; }
.ring-label { font-size: 13px; color: #606266; }

/* 采购员 */
.buyer-bar-row { display: flex; align-items: center; margin-bottom: 12px; }
.buyer-name { width: 60px; font-size: 13px; color: #606266; flex-shrink: 0; }
.buyer-bar-track { flex: 1; height: 28px; background: #f5f7fa; border-radius: 6px; overflow: hidden; margin: 0 12px; }
.buyer-bar-fill { height: 100%; border-radius: 6px; display: flex; align-items: center; padding: 0 10px; min-width: 60px; transition: width 1s ease; }
.buyer-bar-label { font-size: 12px; color: white; font-weight: 500; white-space: nowrap; }

.quick-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.quick-actions .el-button { flex: 1; min-width: 140px; height: 48px; border-radius: 8px; font-weight: 500; }
</style>
