import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Chip,
  Button,
  CircularProgress,
  Alert,
  AlertTitle
} from '@mui/material';
import {
  Email as EmailIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { api } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalEmails: 0,
    processedEmails: 0,
    pendingDeployments: 0,
    successfulDeployments: 0,
    failedDeployments: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    status: 'loading',
    message: 'Checking system status...'
  });

  // Mock data for development
  const mockStats = {
    totalEmails: 42,
    processedEmails: 38,
    pendingDeployments: 2,
    successfulDeployments: 30,
    failedDeployments: 6
  };

  const mockActivities = [
    { id: 1, type: 'deployment', status: 'success', message: 'Successfully deployed app-1', timestamp: '2023-06-20T10:30:00Z' },
    { id: 2, type: 'email', status: 'received', message: 'Received new email from user@example.com', timestamp: '2023-06-20T10:25:00Z' },
    { id: 3, type: 'deployment', status: 'failed', message: 'Failed to deploy app-2: Missing dependencies', timestamp: '2023-06-20T09:45:00Z' },
    { id: 4, type: 'email', status: 'processed', message: 'Processed email from dev@example.com', timestamp: '2023-06-20T09:30:00Z' },
    { id: 5, type: 'system', status: 'warning', message: 'High CPU usage detected', timestamp: '2023-06-20T09:15:00Z' },
  ];

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // In a real app, this would be API calls to your backend
        // const statsResponse = await api.get('/api/dashboard/stats');
        // const activitiesResponse = await api.get('/api/dashboard/activities');
        // const statusResponse = await api.get('/api/status');
        
        // Mock API responses
        setTimeout(() => {
          setStats(mockStats);
          setRecentActivities(mockActivities);
          setSystemStatus({
            status: 'operational',
            message: 'All systems operational'
          });
          setLoading(false);
        }, 1000);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
        setSystemStatus({
          status: 'error',
          message: 'Unable to connect to the server'
        });
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleRefresh = () => {
    // Force refresh data
    window.location.reload();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
      default:
        return <InfoIcon color="info" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* System Status Alert */}
      <Alert 
        severity={systemStatus.status === 'operational' ? 'success' : systemStatus.status}
        sx={{ mb: 3 }}
      >
        <AlertTitle>
          {systemStatus.status === 'operational' 
            ? 'All Systems Operational' 
            : systemStatus.status === 'error' 
              ? 'System Error' 
              : 'System Warning'}
        </AlertTitle>
        {systemStatus.message}
      </Alert>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Emails</Typography>
              <Typography variant="h4">{stats.totalEmails}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Processed</Typography>
              <Typography variant="h4">{stats.processedEmails}</Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={(stats.processedEmails / Math.max(stats.totalEmails, 1)) * 100} 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Pending Deployments</Typography>
              <Typography variant="h4">{stats.pendingDeployments}</Typography>
              <Chip 
                label="View" 
                size="small" 
                color="primary" 
                variant="outlined" 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Successful Deployments</Typography>
              <Typography variant="h4">{stats.successfulDeployments}</Typography>
              <Chip 
                label={`${Math.round((stats.successfulDeployments / Math.max(stats.processedEmails, 1)) * 100)}%`} 
                size="small" 
                color="success" 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Failed Deployments</Typography>
              <Typography variant="h4">{stats.failedDeployments}</Typography>
              <Chip 
                label={`${Math.round((stats.failedDeployments / Math.max(stats.processedEmails, 1)) * 100)}%`} 
                size="small" 
                color="error" 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper>
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              p={2}
              borderBottom={1}
              borderColor="divider"
            >
              <Typography variant="h6">Recent Activities</Typography>
              <Button 
                size="small" 
                startIcon={<RefreshIcon />}
                onClick={handleRefresh}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
            <List>
              {recentActivities.map((activity) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(activity.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.message}
                      secondary={formatTimestamp(activity.timestamp)}
                    />
                    <Chip 
                      label={activity.type} 
                      size="small" 
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                  </ListItem>
                  <Divider component="li" />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
