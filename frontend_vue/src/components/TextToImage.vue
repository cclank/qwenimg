<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>文生图</span>
        <el-tag>Text to Image</el-tag>
      </div>
    </template>

    <el-form :model="form" label-width="100px">
      <el-form-item label="提示词">
        <el-input
          v-model="form.prompt"
          type="textarea"
          :rows="4"
          placeholder="描述你想生成的图片，例如：一只可爱的小猫咪坐在窗台上，夕阳西下，温暖的光线"
        />
      </el-form-item>

      <el-form-item label="负面提示词">
        <el-input
          v-model="form.negative_prompt"
          type="textarea"
          :rows="2"
          placeholder="描述不想出现的元素（可选）"
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="生成数量">
            <el-input-number v-model="form.n" :min="1" :max="4" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="尺寸">
            <el-select v-model="form.size">
              <el-option label="1024x1024" value="1024*1024" />
              <el-option label="720x1280" value="720*1280" />
              <el-option label="1280x720" value="1280*720" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

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
  negative_prompt: '',
  n: 1,
  size: '1024*1024',
})

async function handleSubmit() {
  if (!form.prompt.trim()) {
    ElMessage.warning('请输入提示词')
    return
  }

  loading.value = true
  try {
    const response = await taskApi.createTask('text_to_image', form, store.sessionId)
    ElMessage.success('任务已创建，正在生成中...')

    // 添加到任务列表
    store.addTask({
      task_id: response.data.task_id,
      task_type: 'text_to_image',
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
  form.negative_prompt = ''
  form.n = 1
  form.size = '1024*1024'
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
