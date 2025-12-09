import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Typography,
  Paper,
  Box,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import { PlayArrow as PlayIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { apiService } from '../services/api';

interface JobRun {
  id: number;
  status: string;
  started_at: string;
  completed_at?: string;
  records_processed: number;
  records_success: number;
  records_failed: number;
  triggered_by: string;
}

interface ETLJob {
  id: number;
  name: string;
  description: string;
  source_table: string;
  dest_table: string;
  load_type: string;
  is_active: boolean;
  aggregation_pipeline?: any;
  masking_config?: any;
  created_at: string;
  updated_at: string;
}

const JobDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<ETLJob | null>(null);
  const [runs, setRuns] = useState<JobRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchJobDetails(parseInt(id));
      fetchJobRuns(parseInt(id));
    }
  }, [id]);

  const fetchJobDetails = async (jobId: number) => {
    try {
      const response = await apiService.getJob(jobId);
      setJob(response.data);
    } catch (err) {
      setError('Failed to load job details');
      console.error('Job details error:', err);
    }
  };

  const fetchJobRuns = async (jobId: number) => {
    try {
      const response = await apiService.getJobRuns(jobId);
      setRuns(response.data.runs || []);
    } catch (err) {
      console.error('Job runs error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunJob = async () => {
    if (!job) return;
    try {
      await apiService.triggerJobRun(job.id);
      // Refresh job runs
      fetchJobRuns(job.id);
    } catch (err) {
      console.error('Job run error:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return 'success';
      case 'failed': return 'error';
      case 'running': return 'info';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !job) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error || 'Job not found'}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          {job.name}
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            startIcon={<RefreshIcon />}
            onClick={() => fetchJobRuns(job.id)}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleRunJob}
            disabled={!job.is_active}
          >
            Run Job
          </Button>
        </Box>
      </Box>

      {/* Job Details */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Job Configuration
        </Typography>
        
        <Box display="flex" flexDirection="column" gap={2}>
          <Box>
            <Typography variant="subtitle2" color="textSecondary">
              Description
            </Typography>
            <Typography variant="body1">
              {job.description || 'No description provided'}
            </Typography>
          </Box>
          
          <Box display="flex" gap={4}>
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Source Table
              </Typography>
              <Typography variant="body1">{job.source_table}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Destination Table
              </Typography>
              <Typography variant="body1">{job.dest_table}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Load Type
              </Typography>
              <Chip label={job.load_type} size="small" />
            </Box>
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Status
              </Typography>
              <Chip 
                label={job.is_active ? 'Active' : 'Inactive'} 
                color={job.is_active ? 'success' : 'default'}
                size="small" 
              />
            </Box>
          </Box>

          {job.aggregation_pipeline && (
            <Box>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Aggregation Pipeline
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                  {JSON.stringify(job.aggregation_pipeline, null, 2)}
                </pre>
              </Paper>
            </Box>
          )}

          {job.masking_config && (
            <Box>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Masking Configuration
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                  {JSON.stringify(job.masking_config, null, 2)}
                </pre>
              </Paper>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Job Runs */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Execution History
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Run ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Completed</TableCell>
                <TableCell>Records Processed</TableCell>
                <TableCell>Success</TableCell>
                <TableCell>Failed</TableCell>
                <TableCell>Triggered By</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="textSecondary">
                      No job runs found. Run this job to see execution history.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                runs.map((run) => (
                  <TableRow key={run.id} hover>
                    <TableCell>{run.id}</TableCell>
                    <TableCell>
                      <Chip 
                        label={run.status} 
                        color={getStatusColor(run.status)}
                        size="small" 
                      />
                    </TableCell>
                    <TableCell>{formatDate(run.started_at)}</TableCell>
                    <TableCell>
                      {run.completed_at ? formatDate(run.completed_at) : '-'}
                    </TableCell>
                    <TableCell>{run.records_processed}</TableCell>
                    <TableCell>{run.records_success}</TableCell>
                    <TableCell>{run.records_failed}</TableCell>
                    <TableCell>
                      <Chip label={run.triggered_by} size="small" variant="outlined" />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default JobDetails;