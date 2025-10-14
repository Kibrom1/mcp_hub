import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link,
  Tabs,
  Tab,
  Paper,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Home as HomeIcon,
  Build as BuildIcon,
  NavigateNext as NavigateNextIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

function Tools() {
  const [selectedTool, setSelectedTool] = useState(null);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [toolArguments, setToolArguments] = useState({});
  const [executionResult, setExecutionResult] = useState(null);
  const [selectedServer, setSelectedServer] = useState('all');
  const [activeTab, setActiveTab] = useState(0);
  const queryClient = useQueryClient();
  
  // Collapsible sections state
  const [expandedServers, setExpandedServers] = useState({});
  const [allServersExpanded, setAllServersExpanded] = useState(false);

  // Fetch tools (now grouped by server)
  const { data: toolsData, isLoading: toolsLoading } = useQuery({
    queryKey: ['tools'],
    queryFn: () => api.get('/api/tools/'),
  });

  // Execute tool mutation
  const executeToolMutation = useMutation({
    mutationFn: ({ toolName, arguments: args }) => 
      api.post(`/api/tools/${toolName}/execute`, args),
    onSuccess: (data) => {
      setExecutionResult(data);
      setExecuteDialogOpen(true);
    },
    onError: (error) => {
      setExecutionResult({
        success: false,
        error: error.message,
      });
      setExecuteDialogOpen(true);
    },
  });

  const handleToolClick = (tool) => {
    setSelectedTool(tool);
    setToolArguments({});
    setExecutionResult(null);
    setExecuteDialogOpen(true);
  };

  const handleExecuteTool = (tool) => {
    setSelectedTool(tool);
    setToolArguments({});
    setExecutionResult(null);
    setExecuteDialogOpen(true);
  };

  const handleExecute = () => {
    if (!selectedTool) return;
    
    executeToolMutation.mutate({
      toolName: selectedTool.name,
      arguments: toolArguments,
    });
  };

  const handleCloseDialog = () => {
    setExecuteDialogOpen(false);
    setSelectedTool(null);
    setToolArguments({});
    setExecutionResult(null);
  };

  // Collapsible handlers
  const handleToggleServer = (serverName) => {
    setExpandedServers(prev => ({
      ...prev,
      [serverName]: !prev[serverName]
    }));
  };

  const handleToggleAllServers = () => {
    const newExpandedState = !allServersExpanded;
    setAllServersExpanded(newExpandedState);
    
    // Update all servers to the same expanded state
    const serversToUpdate = servers.reduce((acc, server) => {
      acc[server.server] = newExpandedState;
      return acc;
    }, {});
    
    setExpandedServers(serversToUpdate);
  };

  const renderParameterInput = (paramName, paramInfo) => {
    const paramType = paramInfo?.type || 'string';
    const isRequired = paramInfo?.required !== false;
    
    return (
      <TextField
        key={paramName}
        fullWidth
        label={`${paramName} (${paramType})${isRequired ? ' *' : ''}`}
        value={toolArguments[paramName] || ''}
        onChange={(e) => setToolArguments(prev => ({
          ...prev,
          [paramName]: e.target.value
        }))}
        required={isRequired}
        multiline={paramType === 'text' || paramName.toLowerCase().includes('query')}
        rows={paramName.toLowerCase().includes('query') ? 3 : 1}
        sx={{ mb: 2 }}
        helperText={paramInfo?.description || `Enter ${paramName}`}
      />
    );
  };

  const renderExecutionResult = () => {
    if (!executionResult) return null;

    return (
      <Box sx={{ mt: 2 }}>
        <Alert 
          severity={executionResult.success ? 'success' : 'error'}
          icon={executionResult.success ? <SuccessIcon /> : <ErrorIcon />}
          sx={{ mb: 2 }}
        >
          {executionResult.success ? 'Tool executed successfully!' : 'Tool execution failed'}
        </Alert>
        
        {executionResult.result && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Execution Result:
            </Typography>
            <Box 
              sx={{ 
                bgcolor: 'grey.100', 
                p: 2, 
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                overflow: 'auto',
                maxHeight: 300,
              }}
            >
              <pre>{JSON.stringify(executionResult.result, null, 2)}</pre>
            </Box>
          </Box>
        )}
        
        {executionResult.error && (
          <Box>
            <Typography variant="h6" gutterBottom color="error">
              Error:
            </Typography>
            <Typography variant="body2" color="error">
              {executionResult.error}
            </Typography>
          </Box>
        )}
      </Box>
    );
  };

  if (toolsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  const servers = toolsData?.servers || [];

  return (
    <Box>
      {/* Breadcrumb Navigation */}
      <Breadcrumbs 
        separator={<NavigateNextIcon fontSize="small" />} 
        sx={{ mb: 3 }}
        aria-label="breadcrumb"
      >
        <Link 
          underline="hover" 
          color="inherit" 
          href="#" 
          onClick={() => setSelectedServer('all')}
          sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
        >
          <HomeIcon fontSize="small" />
          All Tools
        </Link>
        {selectedServer !== 'all' && (
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <BuildIcon fontSize="small" />
            {selectedServer.charAt(0).toUpperCase() + selectedServer.slice(1)} Server
          </Typography>
        )}
      </Breadcrumbs>

      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Available Tools
      </Typography>
      
      {/* Server Filter Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => {
            setActiveTab(newValue);
            if (newValue === 0) {
              setSelectedServer('all');
            } else {
              setSelectedServer(servers[newValue - 1]?.server || 'all');
            }
          }}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab 
            label="All Servers" 
            icon={<HomeIcon />}
            iconPosition="start"
          />
          {servers.map((server, index) => (
            <Tab 
              key={server.server}
              label={`${server.server.charAt(0).toUpperCase() + server.server.slice(1)}`}
              icon={<BuildIcon />}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>
      
      {/* Summary Stats */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            System Overview
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {toolsData?.total_servers || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  MCP Servers
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {toolsData?.total_tools || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Tools
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {servers.filter(s => s.enabled).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Servers
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Expand/Collapse All Button */}
      {servers.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={allServersExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            onClick={handleToggleAllServers}
            size="small"
          >
            {allServersExpanded ? 'Collapse All' : 'Expand All'}
          </Button>
        </Box>
      )}
      
      {/* Grouped Tools by Server */}
      {servers
        .filter(server => selectedServer === 'all' || server.server === selectedServer)
        .map((server) => {
          const isServerExpanded = expandedServers[server.server] || false;
          
          return (
            <Card key={server.server} sx={{ mb: 3 }}>
              <CardContent>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between', 
                    mb: 2,
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    },
                    p: 1,
                    borderRadius: 1
                  }}
                  onClick={() => handleToggleServer(server.server)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {server.server.charAt(0).toUpperCase() + server.server.slice(1)} Server
                    </Typography>
                    <Chip
                      label={server.enabled ? 'Enabled' : 'Disabled'}
                      color={server.enabled ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {server.uri}
                    </Typography>
                    <IconButton size="small">
                      {isServerExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </Box>
                    </Box>
                
                <Collapse in={isServerExpanded}>
                  <Grid container spacing={2}>
                    {server.tools.map((tool) => (
                <Grid item xs={12} sm={6} md={4} key={tool.name}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 3
                      }
                    }}
                    onClick={() => handleToolClick(tool)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {tool.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {tool.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <Chip
                          label={tool.enabled ? 'Enabled' : 'Disabled'}
                          color={tool.enabled ? 'success' : 'default'}
                          size="small"
                        />
                        <Chip
                          label={`${Object.keys(tool.parameters).length} params`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      <Button
                        variant="contained"
                        startIcon={<PlayIcon />}
                        fullWidth
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToolClick(tool);
                        }}
                      >
                        Execute Tool
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
                    ))}
                  </Grid>
                </Collapse>
              </CardContent>
            </Card>
          );
        })}

      {/* No tools found message */}
      {selectedServer !== 'all' && 
       servers.filter(server => server.server === selectedServer).length === 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No tools found for {selectedServer} server
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This server may not have any tools configured or may be disabled.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Tool Execution Dialog */}
      <Dialog 
        open={executeDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Execute Tool: {selectedTool?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTool && (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedTool.description}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Server: {selectedTool.server}
              </Typography>
              
              {Object.keys(selectedTool.parameters).length > 0 ? (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Parameters:
                  </Typography>
                  {Object.entries(selectedTool.parameters).map(([paramName, paramInfo]) => 
                    renderParameterInput(paramName, paramInfo)
                  )}
                </Box>
              ) : (
                <Alert severity="info" sx={{ mb: 2 }}>
                  This tool doesn't require any parameters.
                </Alert>
              )}
              
              {renderExecutionResult()}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Close
          </Button>
          {!executionResult && (
            <Button 
              onClick={handleExecute}
              variant="contained"
              disabled={executeToolMutation.isPending}
              startIcon={executeToolMutation.isPending ? <CircularProgress size={16} /> : <PlayIcon />}
            >
              {executeToolMutation.isPending ? 'Executing...' : 'Execute'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Tools;
