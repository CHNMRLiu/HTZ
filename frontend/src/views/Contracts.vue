<template>
  <div class="page-wrapper">
    <div class="page-header">
      <div class="page-header-left">
        <h2>合同管理</h2>
        <p class="page-desc">管理所有供应合同信息</p>
      </div>
      <div class="page-header-right">
        <el-button plain @click="downloadTemplate"><el-icon><Document /></el-icon> 下载模板</el-button>
        <el-upload :action="null" :http-request="handleImport" :show-file-list="false" accept=".xlsx,.xls" style="display:inline-block">
          <el-button type="success" plain><el-icon><Upload /></el-icon> 导入</el-button>
        </el-upload>
        <el-button type="warning" plain @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
        <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增合同</el-button>
      </div>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-input v-model="query.keyword" placeholder="搜索合同号、内容、采购员..." clearable @clear="loadData" @keyup.enter="loadData" class="search-input">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="query.status" placeholder="合同状态" clearable @change="loadData" class="filter-select">
          <el-option label="进行中" value="进行中" />
          <el-option label="待开票" value="待开票" />
          <el-option label="待回款" value="待回款" />
          <el-option label="已完结" value="已完结" />
        </el-select>
        <el-button @click="loadData">查询</el-button>
      </div>

      <el-table :data="list" stripe v-loading="loading" class="data-table"
        :header-cell-style="{ background: '#fafafa', color: '#303133', fontWeight: 600 }"
        :row-class-name="tableRowClassName">
        <el-table-column prop="seq" label="序号" width="70" align="center" />
        <el-table-column prop="contract_no" label="合同号" width="160">
          <template #default="{ row }">
            <span class="contract-no-link" @click="$router.push(`/contracts/${row.id}`)">{{ row.contract_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="contract_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTag(row.contract_type)">{{ row.contract_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sign_date" label="签订日期" width="100" />
        <el-table-column label="到期日期" width="100">
          <template #default="{ row }">
            <span :class="{ 'expire-warning': isExpiring(row.end_date), 'expired': isExpired(row.end_date) }">
              {{ row.end_date || '-' }}
              <el-icon v-if="isExpired(row.end_date)"><WarningFilled /></el-icon>
              <el-icon v-else-if="isExpiring(row.end_date)"><Bell /></el-icon>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="销售金额" width="130" align="right">
          <template #default="{ row }"><span class="sales-text">¥{{ fm(row.amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="purchase_amount" label="采购金额" width="130" align="right">
          <template #default="{ row }"><span class="purchase-text">¥{{ fm(row.purchase_amount) }}</span></template>
        </el-table-column>
        <el-table-column label="利润" width="110" align="right">
          <template #default="{ row }">
            <span :class="(row.amount||0) - (row.purchase_amount||0) >= 0 ? 'profit-positive' : 'profit-negative'">
              ¥{{ fm((row.amount||0) - (row.purchase_amount||0)) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buyer" label="采购员" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.buyer" class="buyer-tag" :style="{ background: buyerColor(row.buyer) }">{{ row.buyer }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="80" align="center" />
        <el-table-column label="进度" width="140" align="center">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-label">订{{ row.order_progress || 0 }}%</span>
              <el-progress :percentage="row.order_progress || 0" :stroke-width="6" :show-text="false" :color="progressColor(row.order_progress)" />
              <span class="progress-label">交{{ row.delivery_progress || 0 }}%</span>
              <el-progress :percentage="row.delivery_progress || 0" :stroke-width="6" :show-text="false" :color="progressColor(row.delivery_progress)" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-btns">
              <el-tooltip content="查看明细" placement="top">
                <el-button size="small" type="primary" :icon="List" circle @click="$router.push(`/contracts/${row.id}`)" />
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button size="small" type="warning" :icon="Edit" circle @click="showDialog(row)" />
              </el-tooltip>
              <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-tooltip content="删除" placement="top">
                    <el-button size="small" type="danger" :icon="Delete" circle />
                  </el-tooltip>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <span class="total-info">共 {{ total }} 条记录</span>
        <el-pagination v-model:current-page="query.page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="loadData" />
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑合同' : '新增合同'" width="800px" destroy-on-close>
      <el-form :model="form" label-width="90px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="序号"><el-input-number v-model="form.seq" :min="1" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="合同号"><el-input v-model="form.contract_no" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="合同类型">
              <el-select v-model="form.contract_type" style="width:100%">
                <el-option label="采购" value="采购" /><el-option label="销售" value="销售" />
                <el-option label="劳务" value="劳务" /><el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="签订日期"><el-input v-model="form.sign_date" placeholder="2025.1.3" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="履约开始"><el-input v-model="form.start_date" placeholder="2025.1.3" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="到期日期">
              <el-input v-model="form.end_date" placeholder="2025.12.31">
                <template #suffix>
                  <el-icon v-if="isExpired(form.end_date)" style="color:#f56c6c"><WarningFilled /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="销售金额"><el-input-number v-model="form.amount" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="采购金额"><el-input-number v-model="form.purchase_amount" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="税率%"><el-input-number v-model="form.tax_rate" :precision="2" :min="0" :max="100" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="合同状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option label="进行中" value="进行中" /><el-option label="待开票" value="待开票" />
                <el-option label="待回款" value="待回款" /><el-option label="已完结" value="已完结" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8"><el-form-item label="采购员"><el-input v-model="form.buyer" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="归属部门"><el-input v-model="form.department" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="甲方"><el-input v-model="form.party_a" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="乙方"><el-input v-model="form.party_b" /></el-form-item></el-col>
          <el-col :span="8">
            <el-form-item label="订货进度%">
              <el-input-number v-model="form.order_progress" :min="0" :max="100" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="交货进度%">
              <el-input-number v-model="form.delivery_progress" :min="0" :max="100" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="16"><el-form-item label="合同内容"><el-input v-model="form.content" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保 存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Upload, Download, Search, List, Edit, Delete, Document, WarningFilled, Bell } from '@element-plus/icons-vue'
import api from '../api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)
const query = reactive({ keyword: '', status: '', page: 1 })
const form = reactive({
  seq: null, contract_no: '', contract_type: '采购',
  sign_date: '', start_date: '', end_date: '',
  amount: null, purchase_amount: 0, tax_rate: 0,
  status: '进行中', buyer: '', department: '',
  party_a: '', party_b: '', content: '', invoice_info: '',
  order_progress: 0, delivery_progress: 0
})

const fm = (v) => (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })

const statusType = (s) => ({
  '进行中': 'primary', '待开票': 'warning', '待回款': 'info', '已完结': 'success'
}[s] || 'primary')

const typeTag = (t) => ({
  '采购': '', '销售': 'success', '劳务': 'warning', '其他': 'info'
}[t] || '')

// 到期提醒
const isExpired = (end) => {
  if (!end) return false
  const d = new Date(end.replace(/\./g, '-'))
  return !isNaN(d) && d < new Date()
}
const isExpiring = (end) => {
  if (!end) return false
  const d = new Date(end.replace(/\./g, '-'))
  if (isNaN(d)) return false
  const diff = (d - new Date()) / (1000 * 60 * 60 * 24)
  return diff > 0 && diff <= 30
}

const tableRowClassName = ({ row }) => {
  if (isExpired(row.end_date)) return 'row-expired'
  if (isExpiring(row.end_date)) return 'row-expiring'
  return ''
}

// 采购员颜色自动生成
const buyerColorPalette = [
  '#409EFF', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#b37feb',
  '#13c2c2', '#eb2f96', '#fa8c16', '#52c41a', '#722ed1', '#2f54eb'
]
const buyerColorMap = {}
let colorIndex = 0
const buyerColor = (name) => {
  if (!name) return '#c0c4cc'
  if (!buyerColorMap[name]) {
    buyerColorMap[name] = buyerColorPalette[colorIndex % buyerColorPalette.length]
    colorIndex++
  }
  return buyerColorMap[name]
}

const progressColor = (pct) => {
  if (pct >= 100) return '#67c23a'
  if (pct >= 60) return '#409EFF'
  if (pct >= 30) return '#e6a23c'
  return '#f56c6c'
}

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/contracts', { params: query })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

const showDialog = (row) => {
  editId.value = row?.id || null
  Object.assign(form, row || {
    seq: null, contract_no: '', contract_type: '采购',
    sign_date: '', start_date: '', end_date: '',
    amount: null, purchase_amount: 0, tax_rate: 0,
    status: '进行中', buyer: '', department: '',
    party_a: '', party_b: '', content: '', invoice_info: '',
    order_progress: 0, delivery_progress: 0
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) await api.put(`/contracts/${editId.value}`, form)
    else await api.post('/contracts', form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { saving.value = false }
}

const handleDelete = async (id) => {
  await api.delete(`/contracts/${id}`)
  ElMessage.success('删除成功')
  loadData()
}

const handleImport = async (opt) => {
  const fd = new FormData(); fd.append('file', opt.file)
  const { data } = await api.post('/import/contracts', fd)
  ElMessage.success(`成功导入 ${data.imported} 条`)
  loadData()
}

const handleExport = () => {
  const a = document.createElement('a')
  a.href = '/api/export/contracts'
  a.click()
}

const downloadTemplate = () => {
  const a = document.createElement('a')
  a.href = '/api/template/contracts'
  a.click()
}

onMounted(loadData)
</script>

<style scoped>
.page-wrapper { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 20px; font-weight: 600; color: #1d1e2c; margin: 0; }
.page-desc { font-size: 13px; color: #909399; margin-top: 4px; }
.page-header-right { display: flex; gap: 8px; }
.card { background: #fff; border-radius: 12px; box-shadow: var(--card-shadow); padding: 24px; }
.search-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.search-input { width: 280px; }
.filter-select { width: 140px; }
.data-table { border-radius: 8px; overflow: hidden; }

/* 到期提醒样式 */
.expire-warning { color: #e6a23c; font-weight: 600; }
.expired { color: #f56c6c; font-weight: 600; }

/* 行样式 */
:deep(.row-expired) { background: #fef0f0 !important; }
:deep(.row-expiring) { background: #fdf6ec !important; }

.contract-no-link { color: #409EFF; font-weight: 600; cursor: pointer; transition: all 0.2s; border-bottom: 1px dashed transparent; }
.contract-no-link:hover { color: #337ecc; border-bottom-color: #337ecc; }
.sales-text { color: #67c23a; font-weight: 600; font-variant-numeric: tabular-nums; }
.purchase-text { color: #e6a23c; font-weight: 600; font-variant-numeric: tabular-nums; }
.profit-positive { color: #67c23a; font-weight: 600; }
.profit-negative { color: #f56c6c; font-weight: 600; }
.buyer-tag { display: inline-block; padding: 2px 10px; border-radius: 12px; color: #fff; font-size: 12px; font-weight: 500; }
.progress-cell { display: flex; flex-direction: column; gap: 2px; }
.progress-label { font-size: 10px; color: #909399; }
.action-btns { display: flex; gap: 6px; justify-content: center; }
.action-btns .el-button { margin-left: 0; }
.pagination-wrapper { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid #f0f0f0; }
.total-info { font-size: 13px; color: #909399; }
.dialog-form { padding: 10px 0; }
</style>
