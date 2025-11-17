<template>
  <el-card shadow="hover">
    <template #header>
      <span>活动任务 ({{ store.activeTasks.length }})</span>
    </template>

    <el-empty v-if="store.activeTasks.length === 0" description="暂无任务" />

    <div v-else class="task-list">
      <div v-for="task in store.activeTasks" :key="task.task_id" class="task-item">
        <div class="task-header">
          <el-tag :type="getTaskTypeColor(task.task_type)" size="small">
            {{ getTaskTypeName(task.task_type) }}
          </el-tag>
          <el-tag :type="getStatusColor(task.status)" size="small">
            {{ getStatusName(task.status) }}
          </el-tag>
        </div>

        <div class="task-info">
          <div class="task-id">ID: {{ task.task_id.slice(0, 8) }}</div>
          <div class="task-time">{{ formatTime(task.created_at) }}</div>
        </div>

        <el-progress
          v-if="task.status === 'processing'"
          :percentage="task.progress || 0"
          :status="task.progress === 100 ? 'success' : undefined"
        />

        <div v-if="task.status === 'completed' && task.result_url" class="task-result">
          <el-image
            v-if="task.task_type === 'text_to_image'"
            :src="task.result_url"
            fit="cover"
            style="width: 100%; height: 150px"
            :preview-src-list="[task.result_url]"
          />
          <video
            v-else
            :src="task.result_url"
            controls
            style="width: 100%"
          />
        </div>

        <div v-if="task.error_message" class="task-error">
          {{ task.error_message }}
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useAppStore } from '../stores/app'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const store = useAppStore()

function getTaskTypeName(type: string) {
  const names: Record<string, string> = {
    text_to_image: '文生图',
    image_to_video: '图生视频',
    text_to_video: '文生视频',
  }
  return names[type] || type
}

function getTaskTypeColor(type: string) {
  const colors: Record<string, any> = {
    text_to_image: 'primary',
    image_to_video: 'success',
    text_to_video: 'warning',
  }
  return colors[type] || 'info'
}

function getStatusName(status: string) {
  const names: Record<string, string> = {
    pending: '等待中',
    processing: '生成中',
    completed: '已完成',
    failed: '失败',
  }
  return names[status] || status
}

function getStatusColor(status: string) {
  const colors: Record<string, any> = {
    pending: 'info',
    processing: 'primary',
    completed: 'success',
    failed: 'danger',
  }
  return colors[status] || 'info'
}

function formatTime(time: string) {
  return dayjs(time).fromNow()
}
</script>

<style scoped>
.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.task-result {
  margin-top: 12px;
}

.task-error {
  margin-top: 8px;
  padding: 8px;
  background: #fee;
  color: #c00;
  border-radius: 4px;
  font-size: 12px;
}
</style>
