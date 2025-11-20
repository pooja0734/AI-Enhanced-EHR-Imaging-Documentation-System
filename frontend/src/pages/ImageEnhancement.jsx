import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Paper,
  Chip,
  Alert,
  LinearProgress,
  Stack,
  Divider
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-toastify'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CompareIcon from '@mui/icons-material/Compare'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ImageIcon from '@mui/icons-material/Image'
import { imageEnhancementService } from '../services/api'

export default function ImageEnhancement() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [enhancedImage, setEnhancedImage] = useState(null)
  const [modality, setModality] = useState('xray')
  const [loading, setLoading] = useState(false)
  const [metrics, setMetrics] = useState(null)
  const [bedrockAnalysis, setBedrockAnalysis] = useState(null)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.dcm']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0]
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target.result)
        setEnhancedImage(null)
        setMetrics(null)
        setBedrockAnalysis(null)
      }
      reader.readAsDataURL(file)
    },
  })

  const handleEnhance = async () => {
    if (!selectedImage) {
      toast.error('Please upload an image first')
      return
    }

    setLoading(true)
    try {
      // Convert data URL to base64
      const base64 = selectedImage.split(',')[1]
      
      const result = await imageEnhancementService.enhanceImage(base64, modality, true)
      
      if (result.success) {
        setEnhancedImage(`data:image/png;base64,${result.enhanced_image}`)
        setMetrics(result.metrics)
        setBedrockAnalysis(result.bedrock_analysis)
        toast.success('✨ Image enhanced successfully with GenAI!')
      } else {
        toast.error('Enhancement failed')
      }
    } catch (error) {
      console.error('Enhancement error:', error)
      toast.error(`Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" spacing={2} alignItems="center" mb={1}>
          <ImageIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4" sx={{ fontWeight: 700, background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Medical Image Enhancement
          </Typography>
        </Stack>
        <Typography variant="body1" color="text.secondary">
          AI-powered medical imaging analysis and enhancement
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid item xs={12} md={4}>
          <Card elevation={3} sx={{ height: '100%', borderRadius: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                <CloudUploadIcon /> Upload Image
              </Typography>

              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: '2px dashed',
                  borderColor: isDragActive ? '#fff' : 'rgba(255,255,255,0.5)',
                  backgroundColor: isDragActive ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)',
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: '#fff',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    transform: 'scale(1.02)',
                  },
                }}
              >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 56, color: 'rgba(255,255,255,0.9)', mb: 2 }} />
                <Typography variant="body1" gutterBottom sx={{ color: 'white', fontWeight: 500 }}>
                  {isDragActive ? '✨ Drop the image here' : 'Drag & drop or click to upload'}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Supports: PNG, JPG, JPEG, DICOM
                </Typography>
              </Paper>

              <FormControl fullWidth sx={{ mt: 3 }}>
                <InputLabel sx={{ color: 'rgba(255,255,255,0.9)' }}>Image Modality</InputLabel>
                <Select
                  value={modality}
                  label="Image Modality"
                  onChange={(e) => setModality(e.target.value)}
                  sx={{ 
                    backgroundColor: 'rgba(255,255,255,0.1)', 
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.5)' },
                    '& .MuiSvgIcon-root': { color: 'white' }
                  }}
                >
                  <MenuItem value="xray">🩻 X-Ray</MenuItem>
                  <MenuItem value="mri">🧠 MRI</MenuItem>
                  <MenuItem value="ct">💿 CT Scan</MenuItem>
                  <MenuItem value="ultrasound">📡 Ultrasound</MenuItem>
                  <MenuItem value="dxa">🦴 DXA</MenuItem>
                </Select>
              </FormControl>

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : <AutoAwesomeIcon />}
                onClick={handleEnhance}
                disabled={!selectedImage || loading}
                sx={{ 
                  mt: 3, 
                  py: 1.5,
                  backgroundColor: '#fff',
                  color: '#667eea',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                  '&:hover': {
                    backgroundColor: '#f0f0f0',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 20px rgba(0,0,0,0.3)',
                  },
                  '&:disabled': {
                    backgroundColor: 'rgba(255,255,255,0.3)',
                    color: 'rgba(255,255,255,0.6)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {loading ? '✨ Enhancing with GenAI...' : '🚀 Enhance with GenAI'}
              </Button>

              {selectedImage && (
                <Chip 
                  icon={<CheckCircleIcon />} 
                  label="Image Ready" 
                  color="success" 
                  sx={{ mt: 2, width: '100%', color: 'white', fontWeight: 600 }} 
                />
              )}
            </CardContent>
          </Card>

          {/* Metrics Card */}
          {metrics && (
            <Card elevation={3} sx={{ mt: 3, borderRadius: 3, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  📊 Quality Metrics
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Box sx={{ backgroundColor: 'rgba(255,255,255,0.2)', p: 2, borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1, fontWeight: 500 }}>
                      PSNR (Peak Signal-to-Noise Ratio)
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                        {metrics.psnr.toFixed(2)} dB
                      </Typography>
                      <Chip 
                        label={metrics.psnr > 30 ? '✓ Excellent' : metrics.psnr > 25 ? '✓ Good' : 'Fair'} 
                        sx={{ 
                          backgroundColor: 'rgba(255,255,255,0.9)',
                          color: metrics.psnr > 30 ? '#2e7d32' : metrics.psnr > 25 ? '#1976d2' : '#ed6c02',
                          fontWeight: 600
                        }}
                        size="small"
                      />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min((metrics.psnr / 40) * 100, 100)} 
                      sx={{ mt: 1.5, height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.3)' }}
                    />
                  </Box>
                  <Box sx={{ backgroundColor: 'rgba(255,255,255,0.2)', p: 2, borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1, fontWeight: 500 }}>
                      SSIM (Structural Similarity)
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                        {metrics.ssim.toFixed(3)}
                      </Typography>
                      <Chip 
                        label={metrics.ssim > 0.85 ? '✓ Excellent' : metrics.ssim > 0.75 ? '✓ Good' : 'Fair'} 
                        sx={{ 
                          backgroundColor: 'rgba(255,255,255,0.9)',
                          color: metrics.ssim > 0.85 ? '#2e7d32' : metrics.ssim > 0.75 ? '#1976d2' : '#ed6c02',
                          fontWeight: 600
                        }}
                        size="small"
                      />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={metrics.ssim * 100} 
                      sx={{ mt: 1.5, height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.3)' }}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Comparison View */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Image Comparison
                </Typography>
                <Chip 
                  icon={<CompareIcon />} 
                  label="Before & After" 
                  color="primary" 
                  variant="outlined"
                />
              </Box>

              <Grid container spacing={2}>
                {/* Original Image */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 2, height: 400 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                      Original Image
                    </Typography>
                    <Box
                      sx={{
                        height: '90%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#000',
                        borderRadius: 1,
                      }}
                    >
                      {selectedImage ? (
                        <img
                          src={selectedImage}
                          alt="Original"
                          style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain',
                          }}
                        />
                      ) : (
                        <Typography color="textSecondary">
                          No image uploaded
                        </Typography>
                      )}
                    </Box>
                  </Paper>
                </Grid>

                {/* Enhanced Image */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 2, height: 400 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                      Enhanced Image
                    </Typography>
                    <Box
                      sx={{
                        height: '90%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#000',
                        borderRadius: 1,
                      }}
                    >
                      {enhancedImage ? (
                        <img
                          src={enhancedImage}
                          alt="Enhanced"
                          style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain',
                          }}
                        />
                      ) : (
                        <Typography color="textSecondary">
                          {loading ? 'Processing...' : 'Click "Enhance with AI" to generate'}
                        </Typography>
                      )}
                    </Box>
                  </Paper>
                </Grid>
              </Grid>

              {/* Bedrock Analysis */}
              {bedrockAnalysis && (
                <Alert severity="info" sx={{ mt: 2 }} icon={<AutoAwesomeIcon />}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    AI Analysis (Claude 3 Sonnet)
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {bedrockAnalysis.analysis}
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
