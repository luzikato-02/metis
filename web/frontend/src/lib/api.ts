import axios from 'axios'

const API_BASE = '/api'

export interface DataFile {
  id: number
  original_filename: string
  stored_filename: string
  file_type: string
  file_size: number
  category: 'input' | 'output'
  parent_id: number | null
  config_json: string | null
  row_count: number | null
  column_count: number | null
  columns_json: string | null
  status: string
  error_message: string | null
  created_at: string
  processed_at: string | null
}

export interface CleaningConfig {
  rpm_max: number
  efficiency_min: number
  efficiency_max: number
  spindles_per_side: number
  shift_hours: number
  drop_multi_style_shifts: boolean
  output_format?: string
}

export interface ProcessResult {
  message: string
  input_file: DataFile
  output_file: DataFile
  stats: {
    input_rows: number
    output_rows: number
    rows_removed: number
  }
}

export interface FileDataResponse {
  columns: string[]
  data: Record<string, unknown>[]
  pagination: {
    page: number
    per_page: number
    total_rows: number
    total_pages: number
  }
}

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE}/health`)
    return response.data
  },

  // File operations
  listFiles: async (category?: 'input' | 'output'): Promise<DataFile[]> => {
    const params = category ? { category } : {}
    const response = await axios.get(`${API_BASE}/files`, { params })
    return response.data.files
  },

  getFile: async (fileId: number): Promise<DataFile> => {
    const response = await axios.get(`${API_BASE}/files/${fileId}`)
    return response.data.file
  },

  getFileData: async (fileId: number, page = 1, perPage = 50): Promise<FileDataResponse> => {
    const response = await axios.get(`${API_BASE}/files/${fileId}/data`, {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  uploadFile: async (file: File): Promise<DataFile> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.file
  },

  processFile: async (fileId: number, config: CleaningConfig): Promise<ProcessResult> => {
    const response = await axios.post(`${API_BASE}/process/${fileId}`, config)
    return response.data
  },

  deleteFile: async (fileId: number): Promise<void> => {
    await axios.delete(`${API_BASE}/files/${fileId}`)
  },

  downloadFile: (fileId: number): string => {
    return `${API_BASE}/files/${fileId}/download`
  }
}
