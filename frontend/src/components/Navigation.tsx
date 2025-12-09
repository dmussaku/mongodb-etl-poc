import React from 'react';
import { Paper, Tabs, Tab, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import WorkIcon from '@mui/icons-material/Work';
import StorageIcon from '@mui/icons-material/Storage';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const getTabValue = () => {
    if (location.pathname === '/') return 0;
    if (location.pathname.startsWith('/jobs')) return 1;
    if (location.pathname.startsWith('/connections')) return 2;
    return 0;
  };

  return (
    <Paper sx={{ mb: 3 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={getTabValue()} aria-label="navigation tabs">
          <Tab
            icon={<DashboardIcon />}
            label="Dashboard"
            component={Link}
            to="/"
          />
          <Tab
            icon={<WorkIcon />}
            label="ETL Jobs"
            component={Link}
            to="/jobs"
          />
          <Tab
            icon={<StorageIcon />}
            label="Connections"
            component={Link}
            to="/connections"
          />
        </Tabs>
      </Box>
    </Paper>
  );
};

export default Navigation;