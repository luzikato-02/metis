import { useState, useCallback } from 'react'
import { Upload, FileSpreadsheet, Settings, Play, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { api, type DataFile, type CleaningConfig, type ProcessResult } from '@/lib/api'
import { formatBytes } from '@/lib/utils'

export function DataCleaningPage() {
  const [uploadedFile, setUploadedFile] = useState<DataFile | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processResult, setProcessResult] = useState<ProcessResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  // Cleaning configuration
  const [config, setConfig] = useState<CleaningConfig>({
    rpm_max: 10000,
    efficiency_min: 75,
    efficiency_max: 100,
    spindles_per_side: 84,
    shift_hours: 8,
    drop_multi_style_shifts: true,
    output_format: 'csv',
  })

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    setError(null)
    setProcessResult(null)
    setIsUploading(true)

    try {
      console.log('Uploading file:', file.name, file.size, file.type)
      const uploadedFile = await api.uploadFile(file)
      setUploadedFile(uploadedFile)
    } catch (err: unknown) {
      console.error('Upload error:', err)
      // Try to extract error from axios response
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Failed to upload file')
      } else {
        setError(err instanceof Error ? err.message : 'Failed to upload file')
      }
    } finally {
      setIsUploading(false)
    }
  }

  const handleProcess = async () => {
    if (!uploadedFile) return

    setError(null)
    setIsProcessing(true)

    try {
      const result = await api.processFile(uploadedFile.id, config)
      setProcessResult(result)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Processing failed'
      // Try to extract error from axios response
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || errorMessage)
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setUploadedFile(null)
    setProcessResult(null)
    setError(null)
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Data Cleaning</h1>
        <p className="text-muted-foreground">
          Upload production data files and clean them for analysis
        </p>
      </div>

      <div className="grid gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload File
            </CardTitle>
            <CardDescription>
              Drag and drop or select a CSV, Excel, or Parquet file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {isUploading ? (
                <div className="flex flex-col items-center gap-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                  <p>Uploading...</p>
                </div>
              ) : uploadedFile ? (
                <div className="flex flex-col items-center gap-3">
                  <FileSpreadsheet className="h-12 w-12 text-primary" />
                  <div>
                    <p className="font-medium">{uploadedFile.original_filename}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatBytes(uploadedFile.file_size)} • {uploadedFile.row_count} rows • {uploadedFile.column_count} columns
                    </p>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleReset}>
                    Upload Different File
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <Upload className="h-12 w-12 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Drop your file here</p>
                    <p className="text-sm text-muted-foreground">or click to browse</p>
                  </div>
                  <Input
                    type="file"
                    accept=".csv,.xlsx,.xls,.parquet"
                    onChange={handleFileSelect}
                    className="max-w-xs"
                  />
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Configuration Section */}
        {uploadedFile && !processResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Cleaning Configuration
              </CardTitle>
              <CardDescription>
                Adjust parameters for data cleaning
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Max RPM</Label>
                  <Slider
                    min={1000}
                    max={20000}
                    step={100}
                    value={config.rpm_max}
                    onChange={(e) => setConfig({ ...config, rpm_max: Number(e.target.value) })}
                    label={`${config.rpm_max}`}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Efficiency Range (%)</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      value={config.efficiency_min}
                      onChange={(e) => setConfig({ ...config, efficiency_min: Number(e.target.value) })}
                      className="w-20"
                    />
                    <span className="text-muted-foreground">to</span>
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      value={config.efficiency_max}
                      onChange={(e) => setConfig({ ...config, efficiency_max: Number(e.target.value) })}
                      className="w-20"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Spindles per Side</Label>
                  <Input
                    type="number"
                    min={1}
                    max={500}
                    value={config.spindles_per_side}
                    onChange={(e) => setConfig({ ...config, spindles_per_side: Number(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Shift Hours</Label>
                  <Input
                    type="number"
                    min={1}
                    max={24}
                    step={0.5}
                    value={config.shift_hours}
                    onChange={(e) => setConfig({ ...config, shift_hours: Number(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Output Format</Label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={config.output_format}
                    onChange={(e) => setConfig({ ...config, output_format: e.target.value })}
                  >
                    <option value="csv">CSV</option>
                    <option value="xlsx">Excel (XLSX)</option>
                    <option value="parquet">Parquet</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label>Drop Multi-Style Shifts</Label>
                  <div className="flex items-center gap-2 pt-2">
                    <Switch
                      checked={config.drop_multi_style_shifts}
                      onChange={(e) => setConfig({ ...config, drop_multi_style_shifts: e.target.checked })}
                    />
                    <span className="text-sm text-muted-foreground">
                      {config.drop_multi_style_shifts ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Clean Data
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <p>{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {processResult && (
          <Card className="border-green-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                Processing Complete
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="bg-muted rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold">{processResult.stats.input_rows}</p>
                  <p className="text-sm text-muted-foreground">Input Rows</p>
                </div>
                <div className="bg-muted rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-green-600">{processResult.stats.output_rows}</p>
                  <p className="text-sm text-muted-foreground">Output Rows</p>
                </div>
                <div className="bg-muted rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-orange-500">{processResult.stats.rows_removed}</p>
                  <p className="text-sm text-muted-foreground">Rows Removed</p>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="h-8 w-8 text-primary" />
                  <div>
                    <p className="font-medium">{processResult.output_file.original_filename}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatBytes(processResult.output_file.file_size)}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button asChild>
                    <a href={api.downloadFile(processResult.output_file.id)} download>
                      Download
                    </a>
                  </Button>
                  <Button variant="outline" onClick={handleReset}>
                    Process Another
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
