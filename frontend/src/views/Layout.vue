<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-logo" @click="$router.push('/dashboard')">
        <div class="logo-mark">
          <el-icon :size="20"><Document /></el-icon>
        </div>
        <transition name="fade">
          <span v-if="!isCollapse" class="logo-text">台账管理系统</span>
        </transition>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
        :collapse-transition="false"
      >
        <el-menu-item index="/dashboard" class="menu-item">
          <el-icon><DataAnalysis /></el-icon>
          <template #title><span>数据概览</span></template>
        </el-menu-item>
        <el-menu-item index="/contracts" class="menu-item">
          <el-icon><Document /></el-icon>
          <template #title><span>合同管理</span></template>
        </el-menu-item>
        <el-menu-item index="/invoices" class="menu-item">
          <el-icon><Tickets /></el-icon>
          <template #title><span>发票管理</span></template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button :icon="isCollapse ? Expand : Fold" text @click="isCollapse = !isCollapse" class="collapse-btn" />
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="全屏" placement="bottom">
            <el-button :icon="FullScreen" circle text @click="toggleFullscreen" />
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, DataAnalysis, Tickets, Fold, Expand, FullScreen, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const username = localStorage.getItem('username')

const titleMap = {
  '/dashboard': '数据概览',
  '/contracts': '合同管理',
  '/invoices': '发票管理'
}

const currentTitle = computed(() => titleMap[route.path] || '首页')

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    localStorage.clear()
    router.push('/login')
  }
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}
</script>

<style scoped>
.layout-container {
  height: 100%;
}

.sidebar {
  background: linear-gradient(180deg, #1d1e2c 0%, #2c2d3e 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #409EFF, #67c23a);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.logo-text {
  margin-left: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.menu-item {
  border-radius: 8px;
  margin-bottom: 4px;
  height: 44px;
  line-height: 44px;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.menu-item.is-active {
  background: linear-gradient(135deg, #409EFF, #337ecc) !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.collapse-btn {
  width: 100%;
  color: rgba(255, 255, 255, 0.65);
}

.collapse-btn:hover {
  color: #fff;
}

.main-container {
  background: #f0f2f5;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #409EFF, #67c23a);
  color: white;
  font-weight: 600;
}

.user-name {
  margin: 0 8px;
  font-size: 14px;
  color: #303133;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
