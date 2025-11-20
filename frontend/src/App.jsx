import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import ImageEnhancement from './pages/ImageEnhancement'
import ClinicalNotes from './pages/ClinicalNotes'
import ICD10Coding from './pages/ICD10Coding'
import PatientManagement from './pages/PatientManagement'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar toggleSidebar={toggleSidebar} />
      <Sidebar open={sidebarOpen} />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: sidebarOpen ? '240px' : '0px',
          transition: 'margin-left 0.3s',
          backgroundColor: '#f5f5f5',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/image-enhancement" element={<ImageEnhancement />} />
          <Route path="/clinical-notes" element={<ClinicalNotes />} />
          <Route path="/icd10-coding" element={<ICD10Coding />} />
          <Route path="/patients" element={<PatientManagement />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Box>
    </Box>
  )
}

export default App
