<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>历史记录</span>
        <el-button size="small" @click="loadHistory">刷新</el-button>
      </div>
    </template>

    <div class="filters">
      <el-select v-model="filters.type" placeholder="任务类型" clearable @change="loadHistory">
        <el-option label="全部" value="" />
        <el-option label="文生图" value="text_to_image" />
        <el-option label="图生视频" value="image_to_video" />
        <el-option label="文生视频" value="text_to_video" />
      </el-select>

      <el-select v-model="filters.status" placeholder="状态" clearable @change="loadHistory">
        <el-option label="全部" value="" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
    </div>

    <el-table v-loading="loading" :data="history" style="width: 100%">
      <el-table-column prop="task_type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTaskTypeColor(row.task_type)" size="small">
            {{ getTaskTypeName(row.task_type) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusColor(row.status)" size="small">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="结果" width="120">
        <template #default="{ row }">
          <el-button
            v-if="row.result_url"
            size="small"
            @click="previewResult(row)"
          >
            查看
          </el-button>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            type="danger"
            size="small"
            @click="deleteTask(row.task_id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="预览" width="60%">
      <el-image
        v-if="currentPreview?.task_type === 'text_to_image'"
        :src="currentPreview.result_url"
        fit="contain"
        style="width: 100%"
      />
      <video
        v-else-if="currentPreview?.result_url"
        :src="currentPreview.result_url"
        controls
        style="width: 100%"
      />
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '../api'
import type { Task } from '../types'
import dayjs from 'dayjs'

const loading = ref(false)
const history = ref<Task[]>([])
const previewVisible = ref(false)
const currentPreview = ref<Task | null>(null)

const filters = reactive({
  type: '',
  status: '',
})

async function loadHistory() {
  loading.value = true
  try {
    const response = await taskApi.getTasks(filters.type, filters.status)
    history.value = response.data
  } catch (error: any) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

async function deleteTask(taskId: string) {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await taskApi.deleteTask(taskId)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function previewResult(task: Task) {
  currentPreview.value = task
  previewVisible.value = true
}

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
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
