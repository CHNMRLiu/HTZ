<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-header" @click="$router.push('/dashboard')">
        <div class="logo-box">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h5v7h7v9H6z"/>
          </svg>
        </div>
        <transition name="sidebar-text">
          <span v-show="!collapsed" class="logo-title">HTZ 台账</span>
        </transition>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="rgba(255,255,255,0.6)"
        active-text-color="#fff"
        :collapse-transition="false"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path" class="menu-item">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title><span>{{ item.label }}</span></template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-bottom">
        <el-button
          :icon="collapsed ? Expand : Fold"
          text
          class="collapse-btn"
          @click="collapsed = !collapsed"
        />
      </div>
    </el-aside>

    <!-- 主区域 -->
    <el-container class="main-wrap">
      <el-header class="top-bar">
        <div class="top-bar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle !== '数据概览'">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="top-bar-right">
          <el-tooltip content="刷新" placement="bottom">
            <el-button :icon="Refresh" circle text @click="refreshPage" />
          </el-tooltip>
          <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏'" placement="bottom">
            <el-button :icon="FullScreen" circle text @click="toggleFullscreen" />
          </el-tooltip>
          <el-dropdown trigger="click" @command="onCommand">
            <div class="user-chip">
              <el-avatar :size="30" class="user-avatar">{{ userInitial }}</el-avatar>
              <span class="user-name">{{ username }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Document, Tickets, Fold, Expand,
  FullScreen, Refresh, ArrowDown, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const isFullscreen = ref(false)
const username = localStorage.getItem('username') || '用户'
const userInitial = computed(() => username.charAt(0).toUpperCase())

const menuItems = [
  { path: '/dashboard', label: '数据概览', icon: DataAnalysis },
  { path: '/contracts', label: '合同管理', icon: Document },
  { path: '/invoices', label: '发票管理', icon: Tickets },
]

const titleMap = Object.fromEntries(menuItems.map(i => [i.path, i.label]))
const activeMenu = computed(() => {
  if (route.path.startsWith('/contracts/')) return '/contracts'
  return route.path
})
const currentTitle = computed(() => titleMap[activeMenu.value] || '首页')

const refreshPage = () => {
  router.replace({ path: route.fullPath, query: { _t: Date.now() } })
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const onCommand = (cmd) => {
  if (cmd === 'logout') {
    localStorage.clear()
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}
</script>

<style scoped>
.layout {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #14151f 0%, #1c1d2e 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 2px 0 16px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 10;
}

.sidebar-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.logo-box {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #409EFF, #67c23a);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.logo-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px;
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.menu-item {
  border-radius: 8px;
  margin-bottom: 4px;
  height: 42px;
  line-height: 42px;
  transition: all 0.2s;
}

.menu-item:hover {
  background: var(--sidebar-hover) !important;
}

.menu-item.is-active {
  background: linear-gradient(135deg, #409EFF, #337ecc) !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
}

.sidebar-bottom {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.collapse-btn {
  width: 100%;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #fff;
}

.main-wrap {
  background: var(--bg-color);
  min-width: 0;
}

.top-bar {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  z-index: 5;
  height: 52px;
}

.top-bar-left {
  display: flex;
  align-items: center;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 8px;
  transition: background 0.2s;
  margin-left: 4px;
}

.user-chip:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #409EFF, #67c23a);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
}

.user-name {
  font-size: 13px;
  color: var(--text-regular);
  font-weight: 500;
}

.arrow {
  color: #c0c4cc;
  font-size: 12px;
}

.content-area {
  padding: 20px;
  overflow-y: auto;
}

/* sidebar text transition */
.sidebar-text-enter-active, .sidebar-text-leave-active {
  transition: opacity 0.2s;
}
.sidebar-text-enter-from, .sidebar-text-leave-to {
  opacity: 0;
}
</style>
