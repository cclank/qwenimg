<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>图生视频</span>
        <el-tag>Image to Video</el-tag>
      </div>
    </template>

    <el-form :model="form" label-width="100px">
      <el-form-item label="上传图片">
        <el-upload
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept="image/*"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
        </el-upload>
      </el-form-item>

      <el-form-item label="图片预览" v-if="imagePreview">
        <img :src="imagePreview" alt="预览" style="max-width: 300px" />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!imageFile"
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
import { Upload } from '@element-plus/icons-vue'
import { taskApi } from '../api'
import { useAppStore } from '../stores/app'
import type { UploadFile } from 'element-plus'

const store = useAppStore()
const loading = ref(false)
const imageFile = ref<File | null>(null)
const imagePreview = ref('')

const form = reactive({})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    imageFile.value = file.raw
    // 创建预览
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file.raw)
  }
}

async function handleSubmit() {
  if (!imageFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  loading.value = true
  try {
    // 转换为 base64
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target?.result as string
      const response = await taskApi.createTask(
        'image_to_video',
        { image_data: base64 },
        store.sessionId
      )
      ElMessage.success('任务已创建，正在生成中...')

      store.addTask({
        task_id: response.data.task_id,
        task_type: 'image_to_video',
        status: 'pending',
        created_at: new Date().toISOString(),
        params: {},
      })
      loading.value = false
    }
    reader.readAsDataURL(imageFile.value)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建任务失败')
    loading.value = false
  }
}

function handleReset() {
  imageFile.value = null
  imagePreview.value = ''
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
