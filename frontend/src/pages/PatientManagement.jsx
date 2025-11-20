import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  MenuItem,
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import AddIcon from '@mui/icons-material/Add'
import { toast } from 'react-toastify'

// Sample patient data with realistic Indian names
const samplePatients = [
  {
    id: 'P001',
    name: 'Aaryan Sharma',
    age: 45,
    gender: 'Male',
    lastVisit: '2025-11-10',
    status: 'Active',
    imagesProcessed: 12,
    notesGenerated: 8,
  },
  {
    id: 'P002',
    name: 'Sushmita Rao',
    age: 62,
    gender: 'Female',
    lastVisit: '2025-11-11',
    status: 'Active',
    imagesProcessed: 5,
    notesGenerated: 3,
  },
  {
    id: 'P003',
    name: 'Rohan Mehta',
    age: 38,
    gender: 'Male',
    lastVisit: '2025-11-08',
    status: 'Inactive',
    imagesProcessed: 8,
    notesGenerated: 5,
  },
  {
    id: 'P004',
    name: 'Priya Patel',
    age: 29,
    gender: 'Female',
    lastVisit: '2025-11-12',
    status: 'Active',
    imagesProcessed: 15,
    notesGenerated: 11,
  },
  {
    id: 'P005',
    name: 'Vikram Singh',
    age: 54,
    gender: 'Male',
    lastVisit: '2025-11-09',
    status: 'Active',
    imagesProcessed: 7,
    notesGenerated: 6,
  },
  {
    id: 'P006',
    name: 'Ananya Desai',
    age: 41,
    gender: 'Female',
    lastVisit: '2025-11-07',
    status: 'Active',
    imagesProcessed: 9,
    notesGenerated: 7,
  },
]

export default function PatientManagement() {
  const [patients, setPatients] = useState(samplePatients)
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [newPatient, setNewPatient] = useState({
    name: '',
    age: '',
    gender: 'Male',
  })

  const handleViewPatient = (patient) => {
    setSelectedPatient(patient)
    toast.info(`Viewing details for ${patient.name}`)
  }

  const handleAddPatient = () => {
    if (!newPatient.name || !newPatient.age) {
      toast.error('Please fill all required fields')
      return
    }

    const patient = {
      id: `P${String(patients.length + 1).padStart(3, '0')}`,
      name: newPatient.name,
      age: parseInt(newPatient.age),
      gender: newPatient.gender,
      lastVisit: new Date().toISOString().split('T')[0],
      status: 'Active',
      imagesProcessed: 0,
      notesGenerated: 0,
    }

    setPatients([...patients, patient])
    setOpenDialog(false)
    setNewPatient({ name: '', age: '', gender: 'Male' })
    toast.success(`Patient ${patient.name} added successfully!`)
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Patient Management
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{
            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
            boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
            '&:hover': {
              background: 'linear-gradient(45deg, #1976d2 30%, #2196F3 90%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 10px 2px rgba(33, 203, 243, .3)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          Add New Patient
        </Button>
      </Box>

      <Card elevation={3}>
        <CardContent>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.100' }}>
                  <TableCell sx={{ fontWeight: 600 }}>Patient ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Age</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Gender</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Last Visit</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Images</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Notes</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {patients.map((patient) => (
                  <TableRow key={patient.id} hover>
                    <TableCell>{patient.id}</TableCell>
                    <TableCell>{patient.name}</TableCell>
                    <TableCell>{patient.age}</TableCell>
                    <TableCell>{patient.gender}</TableCell>
                    <TableCell>{patient.lastVisit}</TableCell>
                    <TableCell>{patient.imagesProcessed}</TableCell>
                    <TableCell>{patient.notesGenerated}</TableCell>
                    <TableCell>
                      <Chip
                        label={patient.status}
                        color={patient.status === 'Active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View patient details" arrow>
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleViewPatient(patient)}
                          sx={{
                            '&:hover': {
                              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                              color: 'white',
                              transform: 'scale(1.1)',
                            },
                            transition: 'all 0.3s ease',
                          }}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add Patient Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ 
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          color: 'white',
          fontWeight: 600
        }}>
          Add New Patient
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="Patient Name"
                fullWidth
                value={newPatient.name}
                onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
                placeholder="e.g., Aaryan Sharma"
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Age"
                type="number"
                fullWidth
                value={newPatient.age}
                onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                placeholder="e.g., 45"
                required
                inputProps={{ min: 0, max: 120 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Gender"
                select
                fullWidth
                value={newPatient.gender}
                onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}
                required
              >
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button 
            onClick={() => setOpenDialog(false)}
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.08)',
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleAddPatient} 
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1976d2 30%, #2196F3 90%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 10px 2px rgba(33, 203, 243, .3)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            Add Patient
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
