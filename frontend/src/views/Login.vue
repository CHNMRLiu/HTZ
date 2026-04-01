<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="login-card" :class="{ 'shake': shakeCard }">
      <div class="login-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h5v7h7v9H6z"/>
            <path d="M8 13h8v2H8zm0 4h5v2H8z"/>
          </svg>
        </div>
        <h1>HTZ 合同台账</h1>
        <p class="subtitle">Contract & Invoice Management System</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="UserIcon"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            placeholder="请输入密码"
            type="password"
            size="large"
            show-password
            :prefix-icon="LockIcon"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-divider>
          <span style="color: #c0c4cc; font-size: 12px;">默认账号</span>
        </el-divider>
        <p class="hint">admin / admin123</p>
      </div>
    </div>

    <p class="copyright">© 2026 HTZ 合同台账管理系统 · v2.0</p>
  </div>
</template>

<script setup>
import { ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User as UserIcon, Lock as LockIcon } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const shakeCard = ref(false)

const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const { data } = await api.post('/auth/login', form.value)
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('is_admin', data.is_admin)
      ElMessage.success('登录成功')
      router.push('/')
    } catch (e) {
      shakeCard.value = true
      setTimeout(() => { shakeCard.value = false }, 500)
      ElMessage.error(e.response?.data?.detail || '登录失败，请检查账号密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0c0e1a 0%, #1a1c2e 40%, #16213e 70%, #0f3460 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.15;
}

.c1 {
  width: 500px;
  height: 500px;
  background: #409EFF;
  top: -150px;
  right: -100px;
  animation: float 20s infinite ease-in-out;
}

.c2 {
  width: 400px;
  height: 400px;
  background: #67c23a;
  bottom: -100px;
  left: -80px;
  animation: float 25s infinite ease-in-out reverse;
}

.c3 {
  width: 300px;
  height: 300px;
  background: #e6a23c;
  top: 40%;
  left: 60%;
  animation: float 18s infinite ease-in-out 5s;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -40px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(15px, 15px) scale(1.02); }
}

.login-card {
  width: 440px;
  padding: 48px 44px;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255,255,255,0.1);
  position: relative;
  z-index: 1;
  animation: cardIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-card.shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(40px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-6px); }
  20%, 40%, 60%, 80% { transform: translateX(6px); }
}

.login-brand {
  text-align: center;
  margin-bottom: 36px;
}

.brand-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #409EFF, #67c23a);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.35);
  transition: transform 0.3s;
}

.brand-icon:hover {
  transform: scale(1.05) rotate(2deg);
}

.login-brand h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1d1e2c;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 13px;
  color: #909399;
  letter-spacing: 1.5px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e4e7ed inset;
  transition: all 0.25s;
  padding: 4px 12px;
  height: 44px;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary) inset;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
}

.login-btn {
  width: 100%;
  height: 46px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 3px;
  background: linear-gradient(135deg, #409EFF, #337ecc);
  border: none;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.35);
  transition: all 0.3s;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.45);
}

.login-btn:active {
  transform: translateY(0);
}

.login-footer {
  margin-top: 8px;
}

.hint {
  text-align: center;
  font-size: 13px;
  color: #c0c4cc;
  letter-spacing: 1px;
}

.copyright {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.25);
  font-size: 12px;
  z-index: 1;
}
</style>
