<template>
  <div class="page">
    <!-- 页头 -->
    <div class="page-header">
      <div>
        <h2>合同管理</h2>
        <p class="page-desc">管理所有供应合同信息</p>
      </div>
      <div class="page-actions">
        <el-button plain @click="downloadTemplate"><el-icon><Document /></el-icon> 模板</el-button>
        <el-upload :action="null" :http-request="handleImport" :show-file-list="false" accept=".xlsx,.xls" style="display:inline-block">
          <el-button type="success" plain><el-icon><Upload /></el-icon> 导入</el-button>
        </el-upload>
        <el-button type="warning" plain @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
        <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 新增合同</el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="card search-card">
      <el-row :gutter="12">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input v-model="query.keyword" placeholder="搜索合同号、内容、采购员..." clearable @clear="loadData" @keyup.enter="loadData">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :xs="12" :sm="4" :md="3">
          <el-select v-model="query.status" placeholder="状态" clearable @change="loadData" style="width:100%">
            <el-option v-for="s in ['进行中','待开票','待回款','已完结']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="4" :md="3">
          <el-select v-model="query.buyer" placeholder="采购员" clearable filterable @change="loadData" style="width:100%">
            <el-option v-for="b in filters.buyers" :key="b" :label="b" :value="b" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="4" :md="3">
          <el-select v-model="query.contract_type" placeholder="合同类型" clearable @change="loadData" style="width:100%">
            <el-option v-for="t in ['采购','销售','劳务','其他']" :key="t" :label="t" :value="t" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="4" :md="3">
          <el-select v-model="query.department" placeholder="部门" clearable filterable @change="loadData" style="width:100%">
            <el-option v-for="d in filters.departments" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="4" :md="3">
          <el-button @click="loadData" style="width:100%">查询</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 批量操作 -->
    <div class="batch-bar" v-if="selectedIds.length > 0">
      <span>已选 <strong>{{ selectedIds.length }}</strong> 项</span>
      <el-button size="small" type="warning" plain @click="batchStatus('已完结')">设为已完结</el-button>
      <el-button size="small" type="danger" plain @click="batchDelete">批量删除</el-button>
    </div>

    <!-- 表格 -->
    <div class="card">
      <el-table
        :data="list"
        stripe
        v-loading="loading"
        class="data-table"
        @selection-change="onSelect"
        @sort-change="onSort"
        :header-cell-style="{ background: '#fafafa', color: '#303133', fontWeight: 600 }"
        :row-class-name="rowClass"
      >
        <el-table-column type="selection" width="45" align="center" />
        <el-table-column prop="seq" label="序号" width="70" align="center" sortable="custom" />
        <el-table-column prop="contract_no" label="合同号" min-width="160" sortable="custom">
          <template #default="{ row }">
            <span class="link" @click="$router.push(`/contracts/${row.id}`)">{{ row.contract_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="contract_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTag(row.contract_type)">{{ row.contract_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sign_date" label="签订日期" width="100" sortable="custom" />
        <el-table-column label="到期日期" width="100">
          <template #default="{ row }">
            <span :class="{ 'expired': isExpired(row.end_date), 'expiring': isExpiring(row.end_date) }">
              {{ row.end_date || '—' }}
              <el-icon v-if="isExpired(row.end_date)"><WarningFilled /></el-icon>
              <el-icon v-else-if="isExpiring(row.end_date)"><Bell /></el-icon>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="销售金额" width="130" align="right" sortable="custom">
          <template #default="{ row }"><span class="amount-sales">¥{{ fmtMoney(row.amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="purchase_amount" label="采购金额" width="130" align="right" sortable="custom">
          <template #default="{ row }"><span class="amount-purchase">¥{{ fmtMoney(row.purchase_amount) }}</span></template>
        </el-table-column>
        <el-table-column label="利润" width="120" align="right" sortable="custom">
          <template #default="{ row }">
            <span :class="(row.amount - row.purchase_amount) >= 0 ? 'profit-pos' : 'profit-neg'">
              ¥{{ fmtMoney(row.amount - row.purchase_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small" effect="light" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buyer" label="采购员" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.buyer" class="buyer-badge" :style="{ background: buyerColor(row.buyer) }">{{ row.buyer }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="80" align="center" />
        <el-table-column label="进度" width="130" align="center">
          <template #default="{ row }">
            <div class="progress-area">
              <div class="progress-row">
                <span class="plbl">订</span>
                <el-progress :percentage="row.order_progress || 0" :stroke-width="5" :show-text="false" :color="progressColor" />
                <span class="pval">{{ row.order_progress || 0 }}%</span>
              </div>
              <div class="progress-row">
                <span class="plbl">交</span>
                <el-progress :percentage="row.delivery_progress || 0" :stroke-width="5" :show-text="false" :color="progressColor" />
                <span class="pval">{{ row.delivery_progress || 0 }}%</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="{ row }">
            <div class="ops">
              <el-tooltip content="明细" placement="top">
                <el-button size="small" type="primary" :icon="List" circle @click="$router.push(`/contracts/${row.id}`)" />
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-button size="small" type="warning" :icon="Edit" circle @click="openDialog(row)" />
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

      <div class="table-footer">
        <span>共 {{ total }} 条</span>
        <el-pagination
          v-model:current-page="query.page"
          :page-size="query.size"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑合同' : '新增合同'" width="820px" destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="序号"><el-input-number v-model="form.seq" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="合同号" prop="contract_no"><el-input v-model="form.contract_no" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="合同类型">
              <el-select v-model="form.contract_type" style="width:100%">
                <el-option v-for="t in ['采购','销售','劳务','其他']" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="签订日期"><el-input v-model="form.sign_date" placeholder="2025.1.3" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="履约开始"><el-input v-model="form.start_date" placeholder="2025.1.3" /></el-form-item>
          </el-col>
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
          <el-col :span="8">
            <el-form-item label="销售金额"><el-input-number v-model="form.amount" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="采购金额"><el-input-number v-model="form.purchase_amount" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税率%"><el-input-number v-model="form.tax_rate" :precision="2" :min="0" :max="100" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="合同状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="s in ['进行中','待开票','待回款','已完结']" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="采购员"><el-input v-model="form.buyer" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="归属部门"><el-input v-model="form.department" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="甲方"><el-input v-model="form.party_a" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="乙方"><el-input v-model="form.party_b" /></el-form-item>
          </el-col>
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
          <el-col :span="16">
            <el-form-item label="合同内容"><el-input v-model="form.content" type="textarea" :rows="2" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="开票信息">
          <el-input v-model="form.invoice_info" type="textarea" :rows="2" placeholder="开票日期-开票号码（金额）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Upload, Download, Search, List, Edit, Delete,
  Document, WarningFilled, Bell
} from '@element-plus/icons-vue'
import api from '../api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)
const formRef = ref(null)
const selectedIds = ref([])
const filters = ref({ buyers: [], departments: [] })

const query = reactive({ keyword: '', status: '', buyer: '', contract_type: '', department: '', sort_by: 'id', sort_order: 'desc', page: 1, size: 20 })

const defaultForm = () => ({
  seq: null, contract_no: '', contract_type: '采购',
  sign_date: '', start_date: '', end_date: '',
  amount: 0, purchase_amount: 0, tax_rate: 0,
  status: '进行中', buyer: '', department: '',
  party_a: '', party_b: '', content: '', invoice_info: '',
  order_progress: 0, delivery_progress: 0
})
const form = reactive(defaultForm())

const formRules = {
  contract_no: [{ required: true, message: '请输入合同号', trigger: 'blur' }],
}

const fmtMoney = (v) => (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
const statusTag = (s) => ({ '进行中': 'primary', '待开票': 'warning', '待回款': 'info', '已完结': 'success' }[s] || 'primary')
const typeTag = (t) => ({ '采购': '', '销售': 'success', '劳务': 'warning', '其他': 'info' }[t] || '')

const isExpired = (d) => {
  if (!d) return false
  const dt = new Date(d.replace(/\./g, '-'))
  return !isNaN(dt) && dt < new Date()
}
const isExpiring = (d) => {
  if (!d) return false
  const dt = new Date(d.replace(/\./g, '-'))
  if (isNaN(dt)) return false
  const diff = (dt - new Date()) / 86400000
  return diff > 0 && diff <= 30
}

const rowClass = ({ row }) => {
  if (isExpired(row.end_date)) return 'row-expired'
  if (isExpiring(row.end_date)) return 'row-expiring'
  return ''
}

const progressColor = (pct) => {
  if (pct >= 100) return '#67c23a'
  if (pct >= 60) return '#409EFF'
  if (pct >= 30) return '#e6a23c'
  return '#f56c6c'
}

const colors = ['#409EFF', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#b37feb', '#13c2c2', '#eb2f96', '#fa8c16', '#52c41a']
const colorMap = {}
let ci = 0
const buyerColor = (name) => {
  if (!name) return '#c0c4cc'
  if (!colorMap[name]) { colorMap[name] = colors[ci % colors.length]; ci++ }
  return colorMap[name]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...query }
    const { data } = await api.get('/contracts', { params })
    list.value = data.items
    total.value = data.total
  } catch (e) {
    ElMessage.error('加载失败')
  } finally { loading.value = false }
}

const loadFilters = async () => {
  try {
    const { data } = await api.get('/contracts/filters')
    filters.value = data
  } catch (e) {}
}

const onSelect = (rows) => { selectedIds.value = rows.map(r => r.id) }
const onSort = ({ prop, order }) => {
  query.sort_by = prop || 'id'
  query.sort_order = order === 'ascending' ? 'asc' : 'desc'
  loadData()
}

const openDialog = (row) => {
  editId.value = row?.id || null
  Object.assign(form, row ? { ...row } : defaultForm())
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editId.value) {
        await api.put(`/contracts/${editId.value}`, form)
      } else {
        await api.post('/contracts', form)
      }
      ElMessage.success('保存成功')
      dialogVisible.value = false
      loadData()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '保存失败')
    } finally { saving.value = false }
  })
}

const handleDelete = async (id) => {
  await api.delete(`/contracts/${id}`)
  ElMessage.success('删除成功')
  loadData()
}

const batchDelete = async () => {
  await ElMessageBox.confirm('确定删除选中的合同？', '批量删除', { type: 'warning' })
  await api.post('/contracts/batch-delete', { ids: selectedIds.value, status: '' })
  ElMessage.success('批量删除成功')
  loadData()
}

const batchStatus = async (status) => {
  await api.post('/contracts/batch-status', { ids: selectedIds.value, status })
  ElMessage.success('批量更新成功')
  loadData()
}

const handleImport = async (opt) => {
  const fd = new FormData()
  fd.append('file', opt.file)
  try {
    const { data } = await api.post('/import/contracts', fd)
    ElMessage.success(data.msg || `成功导入 ${data.data?.imported || 0} 条`)
    loadData()
  } catch (e) {
    ElMessage.error('导入失败')
  }
}

const handleExport = () => window.open('/api/export/contracts', '_blank')
const downloadTemplate = () => window.open('/api/template/contracts', '_blank')

onMounted(() => { loadData(); loadFilters() })
</script>

<style scoped>
.page { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.page-header h2 { font-size: 20px; font-weight: 600; color: #1d1e2c; margin: 0; }
.page-desc { font-size: 13px; color: #909399; margin-top: 4px; }
.page-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.card {
  background: #fff;
  border-radius: var(--border-radius);
  box-shadow: var(--card-shadow);
  padding: 20px;
  margin-bottom: 16px;
}

.search-card { padding: 16px 20px; }

.batch-bar {
  background: #fff;
  border-radius: var(--border-radius);
  padding: 10px 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--card-shadow);
  font-size: 13px;
  color: var(--text-regular);
}

.data-table { border-radius: 8px; overflow: hidden; }
.link { color: var(--primary); font-weight: 600; cursor: pointer; border-bottom: 1px dashed transparent; transition: all 0.2s; }
.link:hover { color: var(--primary-dark); border-bottom-color: var(--primary-dark); }
.amount-sales { color: #67c23a; font-weight: 600; font-variant-numeric: tabular-nums; }
.amount-purchase { color: #e6a23c; font-weight: 600; font-variant-numeric: tabular-nums; }
.profit-pos { color: #67c23a; font-weight: 600; }
.profit-neg { color: #f56c6c; font-weight: 600; }
.expired { color: #f56c6c; font-weight: 600; }
.expiring { color: #e6a23c; font-weight: 600; }
.buyer-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; color: #fff; font-size: 12px; font-weight: 500; }

:deep(.row-expired) { background: #fef0f0 !important; }
:deep(.row-expiring) { background: #fdf6ec !important; }

.progress-area { display: flex; flex-direction: column; gap: 3px; }
.progress-row { display: flex; align-items: center; gap: 4px; }
.plbl { font-size: 10px; color: #909399; width: 14px; }
.pval { font-size: 10px; color: #909399; width: 30px; text-align: right; }

.ops { display: flex; gap: 6px; justify-content: center; }
.ops .el-button { margin-left: 0; }

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 13px;
  color: #909399;
}
</style>
