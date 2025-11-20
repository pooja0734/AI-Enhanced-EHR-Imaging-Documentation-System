import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  CircularProgress,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  Alert,
} from '@mui/material'
import { toast } from 'react-toastify'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningIcon from '@mui/icons-material/Warning'
import { icd10Service } from '../services/api'

export default function ICD10Coding() {
  const [clinicalText, setClinicalText] = useState('')
  const [suggestedCodes, setSuggestedCodes] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSuggest = async () => {
    if (!clinicalText.trim()) {
      toast.error('Please enter clinical text')
      return
    }

    setLoading(true)
    try {
      const result = await icd10Service.suggestCodes(clinicalText, 5)

      if (result.success) {
        setSuggestedCodes(result.suggested_codes)
        toast.success(`Found ${result.total_suggestions} ICD-10 code suggestions`)
      }
    } catch (error) {
      console.error('Coding error:', error)
      toast.error(`Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success'
    if (confidence >= 0.6) return 'primary'
    if (confidence >= 0.4) return 'warning'
    return 'error'
  }

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.6) return 'Medium'
    if (confidence >= 0.4) return 'Low'
    return 'Very Low'
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        ICD-10 Code Suggestion
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Clinical Text Input
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={15}
                label="Enter Clinical Documentation"
                value={clinicalText}
                onChange={(e) => setClinicalText(e.target.value)}
                placeholder="Patient presents with persistent hypertension. Blood pressure readings consistently elevated at 150/95 mmHg. No response to lifestyle modifications..."
                sx={{ mb: 2 }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
                onClick={handleSuggest}
                disabled={loading || !clinicalText.trim()}
              >
                {loading ? 'Analyzing...' : 'Suggest ICD-10 Codes'}
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
                  AI-powered ICD-10 coding with confidence scores and clinical reasoning
                </Typography>
              </Box>

              {suggestedCodes.length > 0 && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="caption">
                    <strong>Tip:</strong> Review suggested codes and verify against complete clinical documentation before submitting
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Suggested ICD-10 Codes
              </Typography>

              {suggestedCodes.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <AutoAwesomeIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                  <Typography color="textSecondary">
                    {loading
                      ? 'Analyzing clinical text with AI...'
                      : 'Enter clinical text and click "Suggest ICD-10 Codes"'}
                  </Typography>
                </Box>
              ) : (
                <List>
                  {suggestedCodes.map((code, index) => (
                    <Paper
                      key={index}
                      elevation={1}
                      sx={{
                        mb: 2,
                        p: 2,
                        border: '1px solid',
                        borderColor: code.valid ? 'divider' : 'warning.main',
                      }}
                    >
                      <ListItem sx={{ px: 0, alignItems: 'flex-start' }}>
                        <Box sx={{ width: '100%' }}>
                          {/* Code Header */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="h6" color="primary">
                                {code.code}
                              </Typography>
                              {code.valid ? (
                                <CheckCircleIcon color="success" fontSize="small" />
                              ) : (
                                <WarningIcon color="warning" fontSize="small" />
                              )}
                            </Box>
                            <Chip
                              label={`${getConfidenceLabel(code.confidence)} (${(code.confidence * 100).toFixed(0)}%)`}
                              color={getConfidenceColor(code.confidence)}
                              size="small"
                            />
                          </Box>

                          {/* Description */}
                          <Typography variant="body1" sx={{ mb: 1, fontWeight: 500 }}>
                            {code.description}
                          </Typography>

                          {/* Confidence Bar */}
                          <Box sx={{ mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="caption" color="textSecondary">
                                Confidence Score
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {(code.confidence * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={code.confidence * 100}
                              color={getConfidenceColor(code.confidence)}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>

                          {/* Reasoning */}
                          {code.reasoning && (
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', mt: 1 }}>
                              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                                Clinical Reasoning:
                              </Typography>
                              <Typography variant="body2" sx={{ mt: 0.5 }}>
                                {code.reasoning}
                              </Typography>
                            </Paper>
                          )}
                        </Box>
                      </ListItem>
                    </Paper>
                  ))}
                </List>
              )}

              {suggestedCodes.length > 0 && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'warning.lighter', borderRadius: 1 }}>
                  <Typography variant="caption" color="warning.dark">
                    <strong>Disclaimer:</strong> AI-suggested codes should be reviewed by qualified medical coding professionals before submission to ensure accuracy and compliance with billing regulations.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
