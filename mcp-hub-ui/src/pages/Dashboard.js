import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Button,
} from '@mui/material';
import {
  Build as ToolsIcon,
  Storage as ResourcesIcon,
  Chat as ChatIcon,
  Speed as SpeedIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

function Dashboard() {
  const queryClient = useQueryClient();
  
  // Fetch system status
  const { data: status, isLoading: statusLoading, error: statusError } = useQuery({
    queryKey: ['status'],
    queryFn: () => api.get('/api/status'),
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
    retry: 1, // Only retry once
    onError: (error) => {
      console.error('Failed to fetch status:', error);
    }
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries(['status']);
  };

  // Fetch recent activity (mock data for now)
  const recentActivity = [
    { id: 1, action: 'Tool executed', tool: 'query_database', time: '2 minutes ago', status: 'success' },
    { id: 2, action: 'Chat message', content: 'Hello, how can I help?', time: '5 minutes ago', status: 'success' },
    { id: 3, action: 'File created', file: 'report.txt', time: '10 minutes ago', status: 'success' },
    { id: 4, action: 'Tool failed', tool: 'list_tables', time: '15 minutes ago', status: 'error' },
  ];

  const getStatusIcon = (status) => {
    return status === 'success' ? <SuccessIcon color="success" /> : <ErrorIcon color="error" />;
  };

  const getStatusColor = (status) => {
    return status === 'success' ? 'success' : 'error';
  };

  // Show error state if API call fails
  if (statusError) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          Dashboard
        </Typography>
        <Card>
          <CardContent>
            <Typography variant="h6" color="error" gutterBottom>
              Unable to load system status
            </Typography>
            <Typography variant="body2" color="text.secondary">
              The backend API is not responding. Please check if the backend is running.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box>
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: 'text.primary', mb: 1 }}>
                  Dashboard
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '1.1rem' }}>
                  Welcome to your MCP Hub control center. Monitor system status, manage tools, and track activity.
                </Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={handleRefresh}
                disabled={statusLoading}
                sx={{ minWidth: 120 }}
              >
                {statusLoading ? 'Refreshing...' : 'Refresh'}
              </Button>
            </Box>

      {/* System Status Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            },
            transition: 'all 0.3s ease-in-out',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', mr: 2 }}>
                  <ToolsIcon />
                </Avatar>
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
                    {statusLoading ? '...' : status?.tools || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    Available Tools
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={statusLoading ? 0 : (status?.tools || 0) * 10} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            },
            transition: 'all 0.3s ease-in-out',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', mr: 2 }}>
                  <ResourcesIcon />
                </Avatar>
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
                    {statusLoading ? '...' : status?.resources || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    Resources
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={statusLoading ? 0 : (status?.resources || 0) * 20} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            },
            transition: 'all 0.3s ease-in-out',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', mr: 2 }}>
                  <SpeedIcon />
                </Avatar>
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
                    {statusLoading ? '...' : status?.servers || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    Active Servers
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={statusLoading ? 0 : (status?.servers || 0) * 25} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            },
            transition: 'all 0.3s ease-in-out',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', mr: 2 }}>
                  <TrendingIcon />
                </Avatar>
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
                    {statusLoading ? '...' : status?.llm_providers || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    LLM Providers
                  </Typography>
                </Box>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={statusLoading ? 0 : (status?.llm_providers || 0) * 33} 
                sx={{ 
                  height: 6, 
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<ChatIcon />}
                  href="/chat"
                  sx={{ borderRadius: 2 }}
                >
                  Start Chat
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ToolsIcon />}
                  href="/tools"
                  sx={{ borderRadius: 2 }}
                >
                  Browse Tools
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ResourcesIcon />}
                  href="/resources"
                  sx={{ borderRadius: 2 }}
                >
                  Explore Resources
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                System Health
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Chip 
                  label="API" 
                  color="success" 
                  size="small" 
                  icon={<SuccessIcon />}
                />
                <Chip 
                  label="Database" 
                  color="success" 
                  size="small" 
                  icon={<SuccessIcon />}
                />
                <Chip 
                  label="LLM" 
                  color="success" 
                  size="small" 
                  icon={<SuccessIcon />}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                All systems operational
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} divider>
                    <ListItemIcon>
                      {getStatusIcon(activity.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body1">
                            {activity.action}
                          </Typography>
                          <Chip
                            label={activity.status}
                            color={getStatusColor(activity.status)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {activity.tool && `Tool: ${activity.tool}`}
                            {activity.content && `Message: ${activity.content}`}
                            {activity.file && `File: ${activity.file}`}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {activity.time}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                System Info
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Last Updated
                </Typography>
                <Typography variant="body1">
                  {statusLoading ? 'Loading...' : new Date(status?.timestamp).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Uptime
                </Typography>
                <Typography variant="body1">
                  {statusLoading ? 'Loading...' : '99.9%'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Version
                </Typography>
                <Typography variant="body1">
                  v1.0.0
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
