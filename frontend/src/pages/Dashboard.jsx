import React from 'react'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Tooltip,
} from '@mui/material'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import ImageIcon from '@mui/icons-material/Image'
import DescriptionIcon from '@mui/icons-material/Description'
import CodeIcon from '@mui/icons-material/Code'
import PeopleIcon from '@mui/icons-material/People'

// Sample data - updated to match 6 active patients
const enhancementData = [
  { name: 'Jan', images: 12, patient: 'Aaryan' },
  { name: 'Feb', images: 18, patient: 'Sushmita' },
  { name: 'Mar', images: 15, patient: 'Rohan' },
  { name: 'Apr', images: 22, patient: 'Priya' },
  { name: 'May', images: 19, patient: 'Vikram' },
  { name: 'Jun', images: 24, patient: 'Ananya' },
]

const metricsData = [
  { name: 'Week 1', psnr: 28.5, ssim: 0.82 },
  { name: 'Week 2', psnr: 30.2, ssim: 0.85 },
  { name: 'Week 3', psnr: 29.8, ssim: 0.84 },
  { name: 'Week 4', psnr: 31.5, ssim: 0.88 },
]

function StatCard({ title, value, icon, color, subtitle }) {
  return (
    <Tooltip title={`Click to view ${title.toLowerCase()} details`} arrow placement="top">
      <Card 
        sx={{ 
          height: '100%',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,240,255,0.9) 100%)',
          }
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography color="textSecondary" gutterBottom variant="overline">
                {title}
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 600, color }}>
                {value}
              </Typography>
              {subtitle && (
                <Typography variant="caption" color="textSecondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
            <Box
              sx={{
                backgroundColor: `${color}15`,
                borderRadius: 2,
                p: 1.5,
                color,
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: color,
                  color: 'white',
                }
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Tooltip>
  )
}

export default function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Dashboard Overview
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Images Enhanced"
            value="110"
            icon={<ImageIcon sx={{ fontSize: 32 }} />}
            color="#1976d2"
            subtitle="From 6 active patients"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Notes Generated"
            value="48"
            icon={<DescriptionIcon sx={{ fontSize: 32 }} />}
            color="#00897b"
            subtitle="SOAP, Discharge & Radiology"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="ICD-10 Codes"
            value="156"
            icon={<CodeIcon sx={{ fontSize: 32 }} />}
            color="#ed6c02"
            subtitle="AI-powered suggestions"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Patients"
            value="6"
            icon={<PeopleIcon sx={{ fontSize: 32 }} />}
            color="#2e7d32"
            subtitle="All patients active"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Image Enhancement Activity
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={enhancementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="images" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Enhancement Quality Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="psnr"
                    stroke="#1976d2"
                    strokeWidth={2}
                    name="PSNR (dB)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="ssim"
                    stroke="#00897b"
                    strokeWidth={2}
                    name="SSIM"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                System Performance
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">AWS Bedrock API</Typography>
                      <Typography variant="body2" color="success.main">98%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={98} sx={{ height: 8, borderRadius: 4 }} />
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Lambda Functions</Typography>
                      <Typography variant="body2" color="success.main">95%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={95} sx={{ height: 8, borderRadius: 4 }} />
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Storage (S3)</Typography>
                      <Typography variant="body2" color="warning.main">72%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={72} 
                      sx={{ height: 8, borderRadius: 4 }}
                      color="warning"
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
