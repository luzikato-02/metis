import { useState, useEffect } from 'react'
import { FileSpreadsheet, Download, Trash2, Eye, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { api, type DataFile, type FileDataResponse } from '@/lib/api'
import { formatBytes, formatDate } from '@/lib/utils'

function FileList({ 
  files, 
  onView, 
  onDelete, 
  isLoading 
}: { 
  files: DataFile[]
  onView: (file: DataFile) => void
  onDelete: (file: DataFile) => void
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <FileSpreadsheet className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No files found</p>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Filename</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Rows</TableHead>
          <TableHead>Columns</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {files.map((file) => (
          <TableRow key={file.id}>
            <TableCell className="font-medium">{file.original_filename}</TableCell>
            <TableCell>
              <Badge variant="outline">{file.file_type.toUpperCase()}</Badge>
            </TableCell>
            <TableCell>{formatBytes(file.file_size)}</TableCell>
            <TableCell>{file.row_count?.toLocaleString() ?? '-'}</TableCell>
            <TableCell>{file.column_count ?? '-'}</TableCell>
            <TableCell>
              <Badge variant={file.status === 'completed' ? 'success' : 'secondary'}>
                {file.status}
              </Badge>
            </TableCell>
            <TableCell>{formatDate(file.created_at)}</TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="icon" onClick={() => onView(file)}>
                  <Eye className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" asChild>
                  <a href={api.downloadFile(file.id)} download>
                    <Download className="h-4 w-4" />
                  </a>
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-destructive hover:text-destructive"
                  onClick={() => onDelete(file)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

function DataPreview({ 
  file, 
  onClose 
}: { 
  file: DataFile
  onClose: () => void
}) {
  const [data, setData] = useState<FileDataResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    loadData()
  }, [file.id, page])

  const loadData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.getFileData(file.id, page, 25)
      setData(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            {file.original_filename}
          </CardTitle>
          <CardDescription>
            {file.row_count?.toLocaleString()} rows • {file.column_count} columns
          </CardDescription>
        </div>
        <Button variant="outline" onClick={onClose}>Close Preview</Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : error ? (
          <div className="text-center py-12 text-destructive">
            <p>{error}</p>
          </div>
        ) : data ? (
          <div className="space-y-4">
            <div className="overflow-x-auto border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    {data.columns.map((col) => (
                      <TableHead key={col} className="whitespace-nowrap">{col}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.data.map((row, idx) => (
                    <TableRow key={idx}>
                      {data.columns.map((col) => (
                        <TableCell key={col} className="whitespace-nowrap max-w-[200px] truncate">
                          {row[col] !== null && row[col] !== undefined 
                            ? String(row[col]) 
                            : <span className="text-muted-foreground">null</span>
                          }
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {((page - 1) * data.pagination.per_page) + 1} to{' '}
                {Math.min(page * data.pagination.per_page, data.pagination.total_rows)} of{' '}
                {data.pagination.total_rows.toLocaleString()} rows
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm">
                  Page {page} of {data.pagination.total_pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.min(data.pagination.total_pages, p + 1))}
                  disabled={page >= data.pagination.total_pages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}

export function DataTablesPage() {
  const [inputFiles, setInputFiles] = useState<DataFile[]>([])
  const [outputFiles, setOutputFiles] = useState<DataFile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [previewFile, setPreviewFile] = useState<DataFile | null>(null)
  const [activeTab, setActiveTab] = useState('input')

  useEffect(() => {
    loadFiles()
  }, [])

  const loadFiles = async () => {
    setIsLoading(true)
    try {
      const [inputs, outputs] = await Promise.all([
        api.listFiles('input'),
        api.listFiles('output'),
      ])
      setInputFiles(inputs)
      setOutputFiles(outputs)
    } catch (err) {
      console.error('Failed to load files:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (file: DataFile) => {
    if (!confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
      return
    }

    try {
      await api.deleteFile(file.id)
      await loadFiles()
      if (previewFile?.id === file.id) {
        setPreviewFile(null)
      }
    } catch (err) {
      console.error('Failed to delete file:', err)
    }
  }

  const handleView = (file: DataFile) => {
    setPreviewFile(file)
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Data Files</h1>
          <p className="text-muted-foreground">
            View and manage your uploaded and processed files
          </p>
        </div>
        <Button onClick={loadFiles} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {previewFile ? (
        <DataPreview file={previewFile} onClose={() => setPreviewFile(null)} />
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4">
            <TabsTrigger value="input">
              Input Files
              <Badge variant="secondary" className="ml-2">{inputFiles.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="output">
              Output Files
              <Badge variant="secondary" className="ml-2">{outputFiles.length}</Badge>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="input">
            <Card>
              <CardHeader>
                <CardTitle>Uploaded Input Files</CardTitle>
                <CardDescription>
                  Raw data files that have been uploaded for cleaning
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileList
                  files={inputFiles}
                  onView={handleView}
                  onDelete={handleDelete}
                  isLoading={isLoading}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="output">
            <Card>
              <CardHeader>
                <CardTitle>Cleaned Output Files</CardTitle>
                <CardDescription>
                  Processed files ready for analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileList
                  files={outputFiles}
                  onView={handleView}
                  onDelete={handleDelete}
                  isLoading={isLoading}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
