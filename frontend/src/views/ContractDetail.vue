<template>
  <div class="page-wrapper">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="$router.push('/contracts')"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
        <div class="contract-title" v-if="contract">
          <h2>{{ contract.contract_no }}</h2>
          <div class="contract-meta">
            <el-tag :type="statusType(contract.status)" size="small" effect="light" round>{{ contract.status }}</el-tag>
            <span class="meta-item"><el-icon><User /></el-icon> {{ contract.buyer }}</span>
            <span class="meta-item"><el-icon><Calendar /></el-icon> {{ contract.sign_date }}</span>
            <span class="meta-item amount">¥{{ (contract.amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          </div>
        </div>
      </div>
      <div class="page-header-right">
        <el-button plain @click="downloadTemplate"><el-icon><Document /></el-icon> 下载模板</el-button>
        <el-upload :action="null" :http-request="handleImport" :show-file-list="false" accept=".xlsx,.xls" style="display:inline-block">
          <el-button type="success" plain><el-icon><Upload /></el-icon> 导入明细</el-button>
        </el-upload>
        <el-button type="warning" plain @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
        <el-button type="primary" @click="addRow"><el-icon><Plus /></el-icon> 添加</el-button>
        <el-button type="danger" plain @click="saveAll" :loading="saving"><el-icon><Check /></el-icon> 保存全部</el-button>
      </div>
    </div>

    <!-- 汇总 -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="6"><div class="summary-card"><span class="summary-label">明细数量</span><span class="summary-value">{{ items.length }}</span></div></el-col>
      <el-col :span="6"><div class="summary-card sales"><span class="summary-label">销售金额</span><span class="summary-value">¥{{ totalSales.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span></div></el-col>
      <el-col :span="6"><div class="summary-card purchase"><span class="summary-label">采购金额</span><span class="summary-value">¥{{ totalPurchase.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span></div></el-col>
      <el-col :span="6"><div class="summary-card profit" :class="{ negative: profit < 0 }"><span class="summary-label">利润</span><span class="summary-value">¥{{ profit.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span></div></el-col>
    </el-row>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialog" title="编辑明细" width="900px" destroy-on-close>
      <el-form :model="editForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="项目号"><el-input v-model="editForm.item_no" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="物料编码"><el-input v-model="editForm.material_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="单位"><el-input v-model="editForm.unit" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="物料名称"><el-input v-model="editForm.material_name" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="数量"><el-input-number v-model="editForm.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="合同单价"><el-input-number v-model="editForm.contract_price" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="总计（含税）"><el-input-number v-model="editForm.total_with_tax" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="采购价"><el-input-number v-model="editForm.purchase_price" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="总价"><el-input-number v-model="editForm.total_price" :precision="2" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="采购合同号"><el-input v-model="editForm.purchase_contract_no" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="订货单位"><el-input v-model="editForm.order_unit" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="签订日期"><el-input v-model="editForm.sign_date" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="交货期"><el-input v-model="editForm.delivery_date" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="交货情况">
              <el-select v-model="editForm.delivery_status" clearable style="width:100%">
                <el-option label="未交货" value="未交货" /><el-option label="部分交货" value="部分交货" /><el-option label="已交货" value="已交货" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16"><el-form-item label="备注"><el-input v-model="editForm.remark" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 明细表格 -->
    <div class="card">
      <div class="card-header">
        <h3>合同明细 <span class="hint">({{ items.length }} 条 · 点击行可编辑)</span></h3>
      </div>
      <el-table :data="items" stripe v-loading="loading" class="data-table" max-height="600"
        :header-cell-style="{ background: '#e8f0fe', color: '#1a73e8', fontWeight: 600, borderBottom: '2px solid #1a73e8' }"
        show-summary :summary-method="getSummaries"
        @row-click="handleRowClick" highlight-current-row>
        <el-table-column type="index" label="#" width="50" align="center" fixed />
        <el-table-column prop="item_no" label="项目号" width="70" align="center" />
        <el-table-column prop="material_code" label="物料编码" width="120" />
        <el-table-column prop="material_name" label="物料名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="60" align="center" />
        <el-table-column prop="quantity" label="数量" width="70" align="right" />
        <el-table-column prop="contract_price" label="合同单价" width="100" align="right">
          <template #default="{ row }">{{ fm(row.contract_price) }}</template>
        </el-table-column>
        <el-table-column prop="total_with_tax" label="总计（含税）" width="120" align="right">
          <template #default="{ row }"><span class="sales-text">{{ fm(row.total_with_tax) }}</span></template>
        </el-table-column>
        <el-table-column prop="purchase_price" label="采购价" width="100" align="right">
          <template #default="{ row }">{{ fm(row.purchase_price) }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="100" align="right">
          <template #default="{ row }"><span class="purchase-text">{{ fm(row.total_price) }}</span></template>
        </el-table-column>
        <el-table-column prop="purchase_contract_no" label="采购合同号" width="130" />
        <el-table-column prop="order_unit" label="订货单位" width="120" show-overflow-tooltip />
        <el-table-column prop="delivery_status" label="交货情况" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.delivery_status" :type="row.delivery_status==='已交货'?'success':row.delivery_status==='部分交货'?'warning':'info'" size="small">{{ row.delivery_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="delivery_date" label="交货期" width="100" />
        <el-table-column prop="remark" label="备注" width="120" show-overflow-tooltip />
        <el-table-column label="" width="40" fixed="right" align="center">
          <template #default="{ row, $index }">
            <el-popconfirm title="删除？" @confirm="deleteRow(row, $index)">
              <template #reference><el-button size="small" type="danger" :icon="Delete" text circle /></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User, Calendar, Plus, Upload, Download, Check, Delete, Document } from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const contract = ref(null)
const items = ref([])
const loading = ref(false)
const saving = ref(false)
const editDialog = ref(false)
const editForm = reactive({})
const editIndex = ref(-1)

const statusType = (s) => ({
  '进行中': 'primary', '待开票': 'warning', '待回款': 'info', '已完结': 'success'
}[s] || 'primary')
const fm = (v) => v ? '¥' + Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) : '-'

const totalSales = computed(() => items.value.reduce((s, i) => s + (i.total_with_tax || 0), 0))
const totalPurchase = computed(() => items.value.reduce((s, i) => s + (i.total_price || 0), 0))
const profit = computed(() => totalSales.value - totalPurchase.value)

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/contracts/${route.params.id}`)
    contract.value = data
    items.value = (data.items || []).map(i => ({ ...i, _dirty: false, _new: false }))
    console.log('Loaded items:', items.value.length)
  } finally { loading.value = false }
}

const handleRowClick = (row) => {
  editIndex.value = items.value.indexOf(row)
  Object.assign(editForm, { ...row })
  editDialog.value = true
}

const saveEdit = async () => {
  saving.value = true
  try {
    const data = {
      item_no: editForm.item_no, material_code: editForm.material_code,
      material_name: editForm.material_name, unit: editForm.unit,
      quantity: editForm.quantity || 0, contract_price: editForm.contract_price || 0,
      total_with_tax: editForm.total_with_tax || 0, purchase_price: editForm.purchase_price || 0,
      total_price: editForm.total_price || 0, purchase_contract_no: editForm.purchase_contract_no,
      order_unit: editForm.order_unit, sign_date: editForm.sign_date,
      delivery_status: editForm.delivery_status, delivery_date: editForm.delivery_date,
      remark: editForm.remark
    }
    if (editForm._new) {
      const res = await api.post(`/contracts/${route.params.id}/items`, data)
      items.value[editIndex.value] = { ...editForm, id: res.data.id, _new: false, _dirty: false }
    } else {
      await api.put(`/items/${editForm.id}`, data)
      items.value[editIndex.value] = { ...editForm, _dirty: false }
    }
    ElMessage.success('保存成功')
    editDialog.value = false
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { saving.value = false }
}

const addRow = () => {
  const newRow = {
    id: null, _new: true, _dirty: true,
    item_no: '', material_code: '', material_name: '', unit: '',
    quantity: 0, contract_price: 0, total_with_tax: 0,
    purchase_price: 0, total_price: 0,
    purchase_contract_no: '', order_unit: '', sign_date: '',
    delivery_status: '未交货', delivery_date: '', remark: ''
  }
  items.value.push(newRow)
  handleRowClick(newRow)
}

const deleteRow = async (row, index) => {
  if (row.id) {
    await api.delete(`/items/${row.id}`)
    ElMessage.success('已删除')
  }
  items.value.splice(index, 1)
}

const saveAll = async () => {
  saving.value = true
  let saved = 0
  try {
    for (const item of items.value) {
      if (!item._dirty && !item._new) continue
      const data = {
        item_no: item.item_no, material_code: item.material_code,
        material_name: item.material_name, unit: item.unit,
        quantity: item.quantity || 0, contract_price: item.contract_price || 0,
        total_with_tax: item.total_with_tax || 0, purchase_price: item.purchase_price || 0,
        total_price: item.total_price || 0, purchase_contract_no: item.purchase_contract_no,
        order_unit: item.order_unit, sign_date: item.sign_date,
        delivery_status: item.delivery_status, delivery_date: item.delivery_date,
        remark: item.remark
      }
      if (item._new) {
        const res = await api.post(`/contracts/${route.params.id}/items`, data)
        item.id = res.data.id; item._new = false
      } else {
        await api.put(`/items/${item.id}`, data)
      }
      item._dirty = false; saved++
    }
    ElMessage.success(saved > 0 ? `已保存 ${saved} 条` : '没有修改')
  } catch (e) { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

const handleImport = async (opt) => {
  const fd = new FormData(); fd.append('file', opt.file)
  const { data } = await api.post(`/contracts/${route.params.id}/items/import`, fd)
  ElMessage.success(`导入 ${data.imported} 条`)
  loadData()
}

const handleExport = () => {
  const a = document.createElement('a')
  a.href = `/api/contracts/${route.params.id}/items/export`
  a.download = `${contract.value?.contract_no || 'contract'}_明细.xlsx`
  a.click()
}

const downloadTemplate = () => {
  const a = document.createElement('a')
  a.href = '/api/template/items'
  a.download = '合同明细导入模板.xlsx'
  a.click()
}

const getSummaries = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (['quantity', 'total_with_tax', 'total_price'].includes(col.property)) {
      const total = data.reduce((s, r) => s + (Number(r[col.property]) || 0), 0)
      sums[idx] = col.property === 'quantity' ? total : '¥' + total.toLocaleString('zh-CN', { minimumFractionDigits: 2 })
    } else sums[idx] = ''
  })
  return sums
}

onMounted(loadData)
</script>

<style scoped>
.page-wrapper { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-header-left { display: flex; flex-direction: column; gap: 8px; }
.page-header-right { display: flex; gap: 8px; flex-wrap: wrap; }
.contract-title h2 { font-size: 22px; font-weight: 700; color: #1d1e2c; margin: 0; }
.contract-meta { display: flex; align-items: center; gap: 16px; margin-top: 8px; flex-wrap: wrap; }
.meta-item { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #606266; }
.meta-item.amount { font-weight: 600; color: #e6a23c; font-size: 15px; }
.summary-row { margin-bottom: 20px; }
.summary-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: var(--card-shadow); text-align: center; border-left: 4px solid #409EFF; }
.summary-card.sales { border-left-color: #67c23a; }
.summary-card.purchase { border-left-color: #e6a23c; }
.summary-card.profit { border-left-color: #409EFF; }
.summary-card.profit.negative { border-left-color: #f56c6c; }
.summary-card.profit.negative .summary-value { color: #f56c6c; }
.summary-label { display: block; font-size: 13px; color: #909399; margin-bottom: 8px; }
.summary-value { font-size: 22px; font-weight: 700; color: #303133; }
.summary-card.sales .summary-value { color: #67c23a; }
.summary-card.purchase .summary-value { color: #e6a23c; }
.card { background: #fff; border-radius: 12px; box-shadow: var(--card-shadow); overflow: hidden; }
.card-header { padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { font-size: 15px; font-weight: 600; color: #303133; margin: 0; }
.hint { font-size: 13px; color: #909399; font-weight: 400; }
.data-table { border-radius: 8px; }
.data-table :deep(.el-table__row) { cursor: pointer; }
.data-table :deep(.el-table__row:hover) { background: #e8f4ff !important; }
.sales-text { color: #67c23a; font-weight: 600; }
.purchase-text { color: #e6a23c; font-weight: 600; }
</style>
