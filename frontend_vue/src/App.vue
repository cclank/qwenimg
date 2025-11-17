<template>
  <el-container class="app-container">
    <!-- 顶部导航 -->
    <el-header class="app-header">
      <div class="header-left">
        <h1 class="app-title">QwenImg AI 创作平台</h1>
        <el-tag type="info" size="small">阿里云通义万相</el-tag>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Github" link @click="openGithub">
          GitHub
        </el-button>
      </div>
    </el-header>

    <el-container>
      <!-- 左侧菜单 -->
      <el-aside width="200px" class="app-aside">
        <el-menu :default-active="activeMenu" @select="handleMenuSelect">
          <el-menu-item-group title="创作工具">
            <el-menu-item index="text_to_image">
              <el-icon><Picture /></el-icon>
              <span>文生图</span>
            </el-menu-item>
            <el-menu-item index="image_to_video">
              <el-icon><VideoCamera /></el-icon>
              <span>图生视频</span>
            </el-menu-item>
            <el-menu-item index="text_to_video">
              <el-icon><Film /></el-icon>
              <span>文生视频</span>
            </el-menu-item>
          </el-menu-item-group>
          <el-menu-item-group title="管理">
            <el-menu-item index="history">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </el-menu-item>
          </el-menu-item-group>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-main class="app-main">
          <el-row :gutter="24">
            <!-- 左侧主区域 -->
            <el-col :xs="24" :lg="16">
              <component :is="currentComponent" />
            </el-col>

            <!-- 右侧任务面板 -->
            <el-col :xs="24" :lg="8">
              <ActiveTasks />
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Picture, VideoCamera, Film, Clock, Github } from '@element-plus/icons-vue'
import { useAppStore } from './stores/app'
import TextToImage from './components/TextToImage.vue'
import ImageToVideo from './components/ImageToVideo.vue'
import TextToVideo from './components/TextToVideo.vue'
import History from './components/History.vue'
import ActiveTasks from './components/ActiveTasks.vue'

const store = useAppStore()
const activeMenu = ref('text_to_image')

const components: Record<string, any> = {
  text_to_image: TextToImage,
  image_to_video: ImageToVideo,
  text_to_video: TextToVideo,
  history: History,
}

const currentComponent = computed(() => components[activeMenu.value])

function handleMenuSelect(index: string) {
  activeMenu.value = index
}

function openGithub() {
  window.open('https://github.com/cclank/qwenimg', '_blank')
}

onMounted(() => {
  store.connectWebSocket()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.app-aside {
  background: #fff;
  border-right: 1px solid #e0e0e0;
}

.app-main {
  background: #f5f7fa;
  padding: 24px;
}
</style>
