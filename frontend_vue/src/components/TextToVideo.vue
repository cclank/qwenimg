<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>文生视频</span>
        <el-tag>Text to Video</el-tag>
      </div>
    </template>

    <el-form :model="form" label-width="100px">
      <el-form-item label="提示词">
        <el-input
          v-model="form.prompt"
          type="textarea"
          :rows="4"
          placeholder="描述你想生成的视频场景，例如：海边日落，波浪轻轻拍打沙滩"
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!form.prompt"
          @click="handleSubmit"
        >
          开始生成
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { taskApi } from '../api'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const loading = ref(false)

const form = reactive({
  prompt: '',
})

async function handleSubmit() {
  if (!form.prompt.trim()) {
    ElMessage.warning('请输入提示词')
    return
  }

  loading.value = true
  try {
    const response = await taskApi.createTask('text_to_video', form, store.sessionId)
    ElMessage.success('任务已创建，正在生成中...')

    store.addTask({
      task_id: response.data.task_id,
      task_type: 'text_to_video',
      status: 'pending',
      created_at: new Date().toISOString(),
      params: { ...form },
    })
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建任务失败')
  } finally {
    loading.value = false
  }
}

function handleReset() {
  form.prompt = ''
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
