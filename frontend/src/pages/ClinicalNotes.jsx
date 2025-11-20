import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Paper,
  Divider,
  Chip,
} from '@mui/material'
import { toast } from 'react-toastify'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import DownloadIcon from '@mui/icons-material/Download'
import { clinicalNotesService } from '../services/api'

export default function ClinicalNotes() {
  const [noteType, setNoteType] = useState('soap')
  const [patientName, setPatientName] = useState('')
  const [patientId, setPatientId] = useState('')
  const [clinicalFindings, setClinicalFindings] = useState('')
  const [generatedNote, setGeneratedNote] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    if (!patientName || !patientId || !clinicalFindings) {
      toast.error('Please fill in all required fields')
      return
    }

    setLoading(true)
    try {
      const patientInfo = {
        patient_id: patientId,
        name: patientName,
      }

      const findings = clinicalFindings.split('\n').filter(f => f.trim())

      let result
      if (noteType === 'soap') {
        result = await clinicalNotesService.generateSOAPNote(patientInfo, findings)
      } else if (noteType === 'discharge') {
        const admissionData = {
          admission_date: '2025-11-01',
          discharge_date: '2025-11-12',
          hospital_course: clinicalFindings,
          procedures: '',
          medications: '',
        }
        result = await clinicalNotesService.generateDischargeSummary(patientInfo, admissionData)
      } else if (noteType === 'radiology') {
        const imageFindings = { findings: clinicalFindings }
        result = await clinicalNotesService.generateRadiologyReport(imageFindings, 'xray')
      }

      if (result.success) {
        setGeneratedNote(result.content)
        toast.success('Clinical note generated successfully!')
      }
    } catch (error) {
      console.error('Generation error:', error)
      toast.error(`Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedNote)
    toast.success('Copied to clipboard!')
  }

  const handleDownload = () => {
    const element = document.createElement('a')
    const file = new Blob([generatedNote], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `clinical_note_${patientId}_${Date.now()}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
    toast.success('Download started!')
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Clinical Notes Generation
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Patient Information
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Note Type</InputLabel>
                <Select
                  value={noteType}
                  label="Note Type"
                  onChange={(e) => setNoteType(e.target.value)}
                >
                  <MenuItem value="soap">SOAP Note</MenuItem>
                  <MenuItem value="discharge">Discharge Summary</MenuItem>
                  <MenuItem value="radiology">Radiology Report</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Patient Name"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Patient ID"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                multiline
                rows={12}
                label={
                  noteType === 'soap'
                    ? 'Clinical Findings (one per line)'
                    : noteType === 'discharge'
                    ? 'Hospital Course & Procedures'
                    : 'Imaging Findings'
                }
                value={clinicalFindings}
                onChange={(e) => setClinicalFindings(e.target.value)}
                placeholder={
                  noteType === 'soap'
                    ? 'Patient complains of headache\nBP: 140/90 mmHg\nTemp: 98.6°F'
                    : noteType === 'discharge'
                    ? 'Admitted with chest pain...\nTreated with...'
                    : 'Chest X-ray shows...'
                }
                sx={{ mb: 2 }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
                onClick={handleGenerate}
                disabled={loading}
                sx={{
                  background: 'linear-gradient(45deg, #00897b 30%, #26a69a 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #00796b 30%, #00897b 90%)',
                  }
                }}
              >
                {loading ? 'Generating...' : 'Generate with AI'}
              </Button>

              <Box sx={{ mt: 2, p: 2, bgcolor: 'success.lighter', borderRadius: 1 }}>
                <Chip
                  icon={<AutoAwesomeIcon />}
                  label="Amazon Titan GenAI (FREE)"
                  size="small"
                  color="success"
                  sx={{ mb: 1 }}
                />
                <Typography variant="caption" display="block" color="text.secondary">
                  Uses Amazon Titan Text Express for professional medical documentation
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Output Section */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Generated Note
                </Typography>
                {generatedNote && (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={handleCopy}
                    >
                      Copy
                    </Button>
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownload}
                      variant="outlined"
                    >
                      Download
                    </Button>
                  </Box>
                )}
              </Box>

              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  minHeight: 500,
                  backgroundColor: '#fafafa',
                  border: '1px solid',
                  borderColor: 'divider',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  overflowY: 'auto',
                }}
              >
                {generatedNote || (
                  <Typography color="textSecondary" align="center" sx={{ mt: 10 }}>
                    {loading
                      ? 'Generating clinical note with AI...'
                      : 'Fill in patient information and click "Generate with AI"'}
                  </Typography>
                )}
                {generatedNote}
              </Paper>

              {generatedNote && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="caption" color="textSecondary">
                      Generated: {new Date().toLocaleString()}
                    </Typography>
                    <Chip label="AI-Generated" size="small" color="secondary" />
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
