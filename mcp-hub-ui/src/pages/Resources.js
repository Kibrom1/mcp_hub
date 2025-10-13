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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Storage as DatabaseIcon,
  Folder as FolderIcon,
  Memory as MemoryIcon,
  Search as SearchIcon,
  PlayArrow as PlayIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

function Resources() {
  const [selectedResource, setSelectedResource] = useState(null);
  const [queryDialogOpen, setQueryDialogOpen] = useState(false);
  const [sqlQuery, setSqlQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const queryClient = useQueryClient();
  
  // Resource management state
  const [addResourceDialogOpen, setAddResourceDialogOpen] = useState(false);
  const [addServerDialogOpen, setAddServerDialogOpen] = useState(false);
  const [editResourceDialogOpen, setEditResourceDialogOpen] = useState(false);
  const [deleteResourceDialogOpen, setDeleteResourceDialogOpen] = useState(false);
  const [resourceToDelete, setResourceToDelete] = useState(null);
  const [newResource, setNewResource] = useState({
    name: '',
    uri: '',
    server_name: '',
    description: ''
  });
  const [newServer, setNewServer] = useState({
    name: '',
    uri: '',
    enabled: true,
    description: ''
  });
  const [editResource, setEditResource] = useState({
    name: '',
    uri: '',
    server_name: '',
    description: ''
  });

  // Fetch resources
  const { data: resourcesData, isLoading: resourcesLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: () => api.get('/api/resources/'),
  });

  // Execute query mutation
  const executeQueryMutation = useMutation({
    mutationFn: ({ query }) => api.post('/api/tools/query_database/execute', { query }),
    onSuccess: (data) => {
      setQueryResult(data);
    },
    onError: (error) => {
      setQueryResult({
        success: false,
        error: error.message,
      });
    },
  });

  // Fetch servers for dropdowns
  const { data: serversData } = useQuery({
    queryKey: ['servers'],
    queryFn: () => api.get('/api/resources/servers/'),
  });

  // Resource management mutations
  const createResourceMutation = useMutation({
    mutationFn: (resourceData) => api.post('/api/resources/', resourceData),
    onSuccess: () => {
      setAddResourceDialogOpen(false);
      setNewResource({ name: '', uri: '', server_name: '', description: '' });
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries(['resources']);
      queryClient.invalidateQueries(['servers']);
      queryClient.invalidateQueries(['status']);
    },
  });

  const createServerMutation = useMutation({
    mutationFn: (serverData) => api.post('/api/resources/servers/', serverData),
    onSuccess: () => {
      setAddServerDialogOpen(false);
      setNewServer({ name: '', uri: '', enabled: true, description: '' });
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries(['resources']);
      queryClient.invalidateQueries(['servers']);
      queryClient.invalidateQueries(['status']);
    },
  });

  const updateResourceMutation = useMutation({
    mutationFn: ({ resourceName, resourceData }) => 
      api.put(`/api/resources/${resourceName}`, resourceData),
    onSuccess: () => {
      setEditResourceDialogOpen(false);
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries(['resources']);
      queryClient.invalidateQueries(['status']);
    },
  });

  const deleteResourceMutation = useMutation({
    mutationFn: (resourceName) => api.delete(`/api/resources/${resourceName}`),
    onSuccess: () => {
      setDeleteResourceDialogOpen(false);
      setResourceToDelete(null);
      // Invalidate and refetch relevant queries
      queryClient.invalidateQueries(['resources']);
      queryClient.invalidateQueries(['status']);
    },
  });

  const handleResourceClick = (resource) => {
    setSelectedResource(resource);
    if (resource.uri.startsWith('sqlite://')) {
      setQueryDialogOpen(true);
    }
  };

  const handleExecuteQuery = () => {
    if (!sqlQuery.trim()) return;
    
    executeQueryMutation.mutate({ query: sqlQuery });
  };

  const handleCloseDialog = () => {
    setQueryDialogOpen(false);
    setSelectedResource(null);
    setSqlQuery('');
    setQueryResult(null);
  };

  const getResourceIcon = (uri) => {
    if (uri.startsWith('sqlite://')) return <DatabaseIcon />;
    if (uri.startsWith('memory://')) return <MemoryIcon />;
    if (uri.startsWith('/')) return <FolderIcon />;
    return <StorageIcon />;
  };

  const getResourceType = (uri) => {
    if (uri.startsWith('sqlite://')) return 'Database';
    if (uri.startsWith('memory://')) return 'Memory Store';
    if (uri.startsWith('/')) return 'File System';
    return 'Resource';
  };

  // Resource management handlers
  const handleAddResource = () => {
    createResourceMutation.mutate(newResource);
  };

  const handleAddServer = () => {
    createServerMutation.mutate(newServer);
  };

  const handleDeleteResource = (resource) => {
    setResourceToDelete(resource);
    setDeleteResourceDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (resourceToDelete) {
      deleteResourceMutation.mutate(resourceToDelete.name);
    }
  };

  const handleEditResource = (resource) => {
    setEditResource({
      name: resource.name,
      uri: resource.uri,
      server_name: resource.server,
      description: ''
    });
    setEditResourceDialogOpen(true);
  };

  const handleUpdateResource = () => {
    if (editResource.name && editResource.uri && editResource.server_name) {
      updateResourceMutation.mutate({
        resourceName: editResource.name,
        resourceData: {
          name: editResource.name,
          uri: editResource.uri,
          server_name: editResource.server_name,
          description: editResource.description
        }
      });
    }
  };

  const getResourceColor = (uri) => {
    if (uri.startsWith('sqlite://')) return 'primary';
    if (uri.startsWith('memory://')) return 'secondary';
    if (uri.startsWith('/')) return 'success';
    return 'default';
  };

  if (resourcesLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  const resources = resourcesData?.resources || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Resources
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setAddServerDialogOpen(true)}
            size="small"
          >
            Add Server
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setAddResourceDialogOpen(true)}
            size="small"
          >
            Add Resource
          </Button>
        </Box>
      </Box>
      
      {/* Resources Grid */}
      <Grid container spacing={3}>
        {resources.map((resource) => (
          <Grid item xs={12} sm={6} md={4} key={resource.name}>
            <Card 
              sx={{ 
                height: '100%', 
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
              onClick={() => handleResourceClick(resource)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ mr: 2, color: `${getResourceColor(resource.uri)}.main` }}>
                    {getResourceIcon(resource.uri)}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {resource.name}
                    </Typography>
                    <Chip
                      label={getResourceType(resource.uri)}
                      color={getResourceColor(resource.uri)}
                      size="small"
                    />
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {resource.uri}
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip
                    label={resource.enabled ? 'Enabled' : 'Disabled'}
                    color={resource.enabled ? 'success' : 'default'}
                    size="small"
                  />
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="Edit Resource">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditResource(resource);
                        }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Resource">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteResource(resource);
                        }}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
                
                <Button
                  variant="outlined"
                  startIcon={<SearchIcon />}
                  fullWidth
                  sx={{ borderRadius: 2 }}
                >
                  Explore
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Database Query Dialog */}
      <Dialog 
        open={queryDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Database Explorer: {selectedResource?.name}
        </DialogTitle>
        <DialogContent>
          {selectedResource && (
            <Box>
              <Tabs 
                value={activeTab} 
                onChange={(e, newValue) => setActiveTab(newValue)}
                sx={{ mb: 2 }}
              >
                <Tab label="Query" />
                <Tab label="Tables" />
                <Tab label="Schema" />
              </Tabs>

              {activeTab === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    SQL Query
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={sqlQuery}
                    onChange={(e) => setSqlQuery(e.target.value)}
                    placeholder="Enter your SQL query here..."
                    sx={{ mb: 2 }}
                  />
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleExecuteQuery}
                      disabled={!sqlQuery.trim() || executeQueryMutation.isPending}
                      startIcon={executeQueryMutation.isPending ? <CircularProgress size={16} /> : <PlayIcon />}
                    >
                      {executeQueryMutation.isPending ? 'Executing...' : 'Execute Query'}
                    </Button>
                    
                    <Button
                      variant="outlined"
                      onClick={() => setSqlQuery('SELECT * FROM servers LIMIT 10')}
                    >
                      Sample Query
                    </Button>
                  </Box>

                  {queryResult && (
                    <Box>
                      <Alert 
                        severity={queryResult.success ? 'success' : 'error'}
                        sx={{ mb: 2 }}
                      >
                        {queryResult.success ? 'Query executed successfully!' : 'Query failed'}
                      </Alert>
                      
                      {queryResult.result && (
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            Results:
                          </Typography>
                          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                            <Table stickyHeader>
                              <TableHead>
                                <TableRow>
                                  {queryResult.result.columns?.map((column, index) => (
                                    <TableCell key={index} sx={{ fontWeight: 600 }}>
                                      {column}
                                    </TableCell>
                                  ))}
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {queryResult.result.rows?.slice(0, 100).map((row, index) => (
                                  <TableRow key={index}>
                                    {row.map((cell, cellIndex) => (
                                      <TableCell key={cellIndex}>
                                        {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                                      </TableCell>
                                    ))}
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                          
                          {queryResult.result.row_count > 100 && (
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Showing first 100 rows of {queryResult.result.row_count} total rows
                            </Typography>
                          )}
                        </Box>
                      )}
                      
                      {queryResult.error && (
                        <Alert severity="error">
                          {queryResult.error}
                        </Alert>
                      )}
                    </Box>
                  )}
                </Box>
              )}

              {activeTab === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Database Tables
                  </Typography>
                  <Alert severity="info">
                    Use the Query tab to execute "SHOW TABLES" or "SELECT name FROM sqlite_master WHERE type='table'"
                  </Alert>
                </Box>
              )}

              {activeTab === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Database Schema
                  </Typography>
                  <Alert severity="info">
                    Use the Query tab to execute "PRAGMA table_info(table_name)" to get table schema
                  </Alert>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      {/* Add Resource Dialog */}
      <Dialog open={addResourceDialogOpen} onClose={() => setAddResourceDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Resource</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Resource Name"
            value={newResource.name}
            onChange={(e) => setNewResource({ ...newResource, name: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            fullWidth
            label="Resource URI"
            value={newResource.uri}
            onChange={(e) => setNewResource({ ...newResource, uri: e.target.value })}
            sx={{ mb: 2 }}
            placeholder="e.g., https://api.example.com, file:///path/to/file"
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Server</InputLabel>
            <Select
              value={newResource.server_name}
              onChange={(e) => setNewResource({ ...newResource, server_name: e.target.value })}
            >
              {serversData?.servers?.map((server) => (
                <MenuItem key={server.name} value={server.name}>
                  {server.name} ({server.uri})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Description (Optional)"
            value={newResource.description}
            onChange={(e) => setNewResource({ ...newResource, description: e.target.value })}
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddResourceDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAddResource} 
            variant="contained"
            disabled={!newResource.name || !newResource.uri || !newResource.server_name}
          >
            Add Resource
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Server Dialog */}
      <Dialog open={addServerDialogOpen} onClose={() => setAddServerDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Server</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Server Name"
            value={newServer.name}
            onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
            placeholder="e.g., external-api, custom-server"
          />
          <TextField
            fullWidth
            label="Server URI"
            value={newServer.uri}
            onChange={(e) => setNewServer({ ...newServer, uri: e.target.value })}
            sx={{ mb: 2 }}
            placeholder="e.g., https://api.example.com, file:///path"
          />
          <TextField
            fullWidth
            label="Description (Optional)"
            value={newServer.description}
            onChange={(e) => setNewServer({ ...newServer, description: e.target.value })}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddServerDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAddServer} 
            variant="contained"
            disabled={!newServer.name || !newServer.uri}
          >
            Add Server
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Resource Dialog */}
      <Dialog open={editResourceDialogOpen} onClose={() => setEditResourceDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Resource</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Resource Name"
            value={editResource.name}
            onChange={(e) => setEditResource({ ...editResource, name: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
            disabled
          />
          <TextField
            fullWidth
            label="Resource URI"
            value={editResource.uri}
            onChange={(e) => setEditResource({ ...editResource, uri: e.target.value })}
            sx={{ mb: 2 }}
            placeholder="e.g., sqlite:///path/to/db, file:///path/to/files"
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Server</InputLabel>
            <Select
              value={editResource.server_name}
              onChange={(e) => setEditResource({ ...editResource, server_name: e.target.value })}
              label="Server"
            >
              {serversData?.servers?.map((server) => (
                <MenuItem key={server.name} value={server.name}>
                  {server.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Description (Optional)"
            value={editResource.description}
            onChange={(e) => setEditResource({ ...editResource, description: e.target.value })}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditResourceDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleUpdateResource} 
            variant="contained"
            disabled={!editResource.name || !editResource.uri || !editResource.server_name || updateResourceMutation.isLoading}
          >
            {updateResourceMutation.isLoading ? 'Updating...' : 'Update Resource'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Resource Dialog */}
      <Dialog open={deleteResourceDialogOpen} onClose={() => setDeleteResourceDialogOpen(false)}>
        <DialogTitle>Delete Resource</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the resource "{resourceToDelete?.name}"? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteResourceDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleConfirmDelete} 
            variant="contained" 
            color="error"
            disabled={deleteResourceMutation.isLoading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Resources;
