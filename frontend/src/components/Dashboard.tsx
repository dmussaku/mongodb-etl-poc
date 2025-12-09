import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Work as WorkIcon,
  Storage as StorageIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  PlayArrow as RunningIcon
} from '@mui/icons-material';
import { apiService } from '../services/api';

interface HealthStatus {
  status: string;
  checks: {
    postgres: string;
    redis: string;
    rabbitmq: string;
    mongodb: string;
  };
}

interface Stats {
  totalJobs: number;
  activeJobs: number;
  runningJobs: number;
  connections: number;
}

const Dashboard: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [health, jobs, connections] = await Promise.all([
        apiService.getHealth(),
        apiService.getJobs(),
        apiService.getConnections()
      ]);
      
      setHealthStatus(health.data);
      setStats({
        totalJobs: jobs.data.count || 0,
        activeJobs: jobs.data.jobs?.filter((job: any) => job.is_active).length || 0,
        runningJobs: 0, // TODO: Get from job runs
        connections: connections.data.count || 0
      });
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'healthy') return 'success';
    if (status.includes('error')) return 'error';
    return 'warning';
  };

  const getStatusIcon = (status: string) => {
    if (status === 'healthy') return <SuccessIcon color="success" />;
    if (status.includes('error')) return <ErrorIcon color="error" />;
    return <RunningIcon color="warning" />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Box display="flex" gap={3} sx={{ mb: 4, flexWrap: 'wrap' }}>
        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <WorkIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Jobs
                </Typography>
                <Typography variant="h4">
                  {stats?.totalJobs || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <RunningIcon color="warning" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Active Jobs
                </Typography>
                <Typography variant="h4">
                  {stats?.activeJobs || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <RunningIcon color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Running Jobs
                </Typography>
                <Typography variant="h4">
                  {stats?.runningJobs || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        
        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <StorageIcon color="secondary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Connections
                </Typography>
                <Typography variant="h4">
                  {stats?.connections || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Health Status */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Health
        </Typography>
        <Box display="flex" flexDirection="column" gap={2}>
          {healthStatus?.checks && Object.entries(healthStatus.checks).map(([service, status]) => (
            <Box key={service} display="flex" alignItems="center" justifyContent="space-between" sx={{ p: 1, borderRadius: 1, bgcolor: 'grey.50' }}>
              <Box display="flex" alignItems="center">
                {getStatusIcon(status)}
                <Typography variant="body1" sx={{ ml: 1, textTransform: 'capitalize' }}>
                  {service}
                </Typography>
              </Box>
              <Chip 
                label={status === 'healthy' ? 'Healthy' : 'Error'} 
                color={getStatusColor(status)} 
                size="small" 
              />
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;