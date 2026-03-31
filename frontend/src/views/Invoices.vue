<template>
  <div class="page-wrapper">
    <div class="page-header">
      <div class="page-header-left">
        <h2>发票管理</h2>
        <p class="page-desc">管理所有增值税发票信息</p>
      </div>
      <div class="page-header-right">
        <el-button type="warning" plain @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
        <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增发票</el-button>
      </div>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-input v-model="query.keyword" placeholder="搜索发票号、销售方..." clearable @clear="loadData" @keyup.enter="loadData" class="search-input">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button @click="loadData">查询</el-button>
      </div>

      <el-table :data="list" stripe v-loading="loading" class="data-table" :header-cell-style="{ background: '#fafafa', color: '#303133', fontWeight: 600 }">
        <el-table-column prop="invoice_no" label="发票号码" width="210">
          <template #default="{ row }">
            <span class="invoice-no">{{ row.invoice_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="invoice_date" label="开票日期" width="110" />
        <el-table-column prop="amount" label="价税合计" width="140" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ (row.amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="tax_amount" label="税额" width="120" align="right">
          <template #default="{ row }">
            <span class="tax">¥{{ (row.tax_amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="seller" label="销售方" show-overflow-tooltip min-width="180" />
        <el-table-column label="关联合同" width="160">
          <template #default="{ row }">
            <el-tag v-if="row.contract_id && contractsMap[row.contract_id]" type="info" size="small" effect="plain">
              {{ contractsMap[row.contract_id] }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="showDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该发票？" @confirm="handleDelete(row.id)">
              <template #reference><el-button size="small" text type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <span class="total-info">共 {{ total }} 条记录</span>
        <el-pagination v-model:current-page="query.page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="loadData" />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑发票' : '新增发票'" width="600px" destroy-on-close>
      <el-form :model="form" label-width="100px" class="dialog-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发票号码"><el-input v-model="form.invoice_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开票日期"><el-input v-model="form.invoice_date" placeholder="如: 2025.1.13" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价税合计"><el-input-number v-model="form.amount" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="税额"><el-input-number v-model="form.tax_amount" :precision="2" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关联合同">
          <el-select v-model="form.contract_id" filterable clearable placeholder="选择关联合同" style="width:100%">
            <el-option v-for="c in contracts" :key="c.id" :label="`${c.contract_no} — ${c.buyer || '未知'}`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="销售方"><el-input v-model="form.seller" /></el-form-item>
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
import { Plus, Download, Search } from '@element-plus/icons-vue'
import api from '../api'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)
const query = reactive({ keyword: '', page: 1 })
const contracts = ref([])
const contractsMap = ref({})
const form = reactive({ invoice_no: '', invoice_date: '', amount: null, tax_amount: null, contract_id: null, seller: '' })

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/invoices', { params: query })
    list.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

const loadContracts = async () => {
  const { data } = await api.get('/contracts', { params: { size: 1000 } })
  contracts.value = data.items
  data.items.forEach(c => { contractsMap.value[c.id] = c.contract_no })
}

const showDialog = (row) => {
  editId.value = row?.id || null
  Object.assign(form, row || { invoice_no: '', invoice_date: '', amount: null, tax_amount: null, contract_id: null, seller: '' })
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editId.value) await api.put(`/invoices/${editId.value}`, form)
    else await api.post('/invoices', form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { saving.value = false }
}

const handleDelete = async (id) => {
  await api.delete(`/invoices/${id}`)
  ElMessage.success('删除成功')
  loadData()
}

const handleExport = () => window.open('/api/export/invoices', '_blank')

onMounted(() => { loadData(); loadContracts() })
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

.data-table { border-radius: 8px; overflow: hidden; }
.invoice-no { font-weight: 500; color: #67c23a; }
.amount { font-weight: 600; color: #e6a23c; font-variant-numeric: tabular-nums; }
.tax { color: #909399; font-variant-numeric: tabular-nums; }
.text-muted { color: #c0c4cc; }

.pagination-wrapper { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 16px; border-top: 1px solid #f0f0f0; }
.total-info { font-size: 13px; color: #909399; }
.dialog-form { padding: 10px 0; }
</style>
