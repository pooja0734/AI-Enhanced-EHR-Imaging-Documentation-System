import axios from 'axios'

// Get API URL from environment or use default
const API_URL = import.meta.env.VITE_API_URL || 'https://your-api-gateway-url.amazonaws.com/prod'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Image Enhancement Service
export const imageEnhancementService = {
  enhanceImage: async (imageBase64, modality = 'xray', useBedrock = true) => {
    const response = await api.post('/image-enhancement', {
      image_base64: imageBase64,
      modality,
      use_bedrock: useBedrock,
    })
    return response.data
  },
}

// Clinical Notes Service
export const clinicalNotesService = {
  generateSOAPNote: async (patientInfo, findings) => {
    const response = await api.post('/clinical-notes', {
      note_type: 'soap',
      patient_info: patientInfo,
      findings,
    })
    return response.data
  },

  generateDischargeSummary: async (patientInfo, admissionData) => {
    const response = await api.post('/clinical-notes', {
      note_type: 'discharge',
      patient_info: patientInfo,
      admission_data: admissionData,
    })
    return response.data
  },

  generateRadiologyReport: async (imageFindings, modality) => {
    const response = await api.post('/clinical-notes', {
      note_type: 'radiology',
      image_findings: imageFindings,
      modality,
    })
    return response.data
  },
}

// ICD-10 Coding Service
export const icd10Service = {
  suggestCodes: async (clinicalText, topK = 5) => {
    const response = await api.post('/icd10-coding', {
      clinical_text: clinicalText,
      top_k: topK,
    })
    return response.data
  },
}

// Patient Management Service
export const patientService = {
  getPatients: async () => {
    const response = await api.get('/patients')
    return response.data
  },

  getPatient: async (patientId) => {
    const response = await api.get(`/patients/${patientId}`)
    return response.data
  },

  createPatient: async (patientData) => {
    const response = await api.post('/patients', patientData)
    return response.data
  },

  updatePatient: async (patientId, patientData) => {
    const response = await api.put(`/patients/${patientId}`, patientData)
    return response.data
  },
}

export default api
