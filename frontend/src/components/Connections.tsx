import React, { useState, useEffect } from 'react';
import {
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { apiService } from '../services/api';

interface Connection {
  id: number;
  name: string;
  connection_type: string;
  created_at: string;
  updated_at: string;
}

const Connections: React.FC = () => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      setLoading(true);
      const response = await apiService.getConnections();
      setConnections(response.data.connections || []);
    } catch (err) {
      setError('Failed to load connections');
      console.error('Connections fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConnectionTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'mongodb': return 'success';
      case 'postgres': return 'primary';
      case 'mysql': return 'info';
      case 'bigquery': return 'warning';
      case 's3': return 'secondary';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
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
        Database Connections
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {connections.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="textSecondary">
                    No database connections found. Add your first connection to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              connections.map((connection) => (
                <TableRow key={connection.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2">{connection.name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={connection.connection_type} 
                      size="small" 
                      color={getConnectionTypeColor(connection.connection_type)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {formatDate(connection.created_at)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {formatDate(connection.updated_at)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Connections;