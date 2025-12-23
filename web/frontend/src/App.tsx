import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DataCleaningPage } from './pages/DataCleaningPage'
import { DataTablesPage } from './pages/DataTablesPage'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DataCleaningPage />} />
          <Route path="/files" element={<DataTablesPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
