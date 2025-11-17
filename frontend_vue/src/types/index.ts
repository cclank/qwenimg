export interface Task {
  task_id: string
  task_type: 'text_to_image' | 'image_to_video' | 'text_to_video'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  result_url?: string
  error_message?: string
  created_at: string
  params: Record<string, any>
}

export interface WSMessage {
  type: 'task_update' | 'task_complete' | 'task_error'
  task_id: string
  status?: string
  progress?: number
  result_url?: string
  error_message?: string
}
