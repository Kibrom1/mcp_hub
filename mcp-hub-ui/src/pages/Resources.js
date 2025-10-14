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
  Switch,
  FormControlLabel,
  Collapse,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Storage as DatabaseIcon,
  Storage as PostgreSQLIcon,
  Storage as SQLiteIcon,
  Storage as MySQLIcon,
  Folder as FolderIcon,
  Memory as MemoryIcon,
  Search as SearchIcon,
  PlayArrow as PlayIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ChevronRight as ChevronRightIcon,
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
  
  // Collapsible sections state
  const [serversExpanded, setServersExpanded] = useState(true);
  const [resourcesExpanded, setResourcesExpanded] = useState(true);
  const [databasesExpanded, setDatabasesExpanded] = useState(true);
  const [expandedServers, setExpandedServers] = useState({});
  
  // Resource management state
  const [addResourceDialogOpen, setAddResourceDialogOpen] = useState(false);
  const [addServerDialogOpen, setAddServerDialogOpen] = useState(false);
  const [addDatabaseDialogOpen, setAddDatabaseDialogOpen] = useState(false);
  const [editResourceDialogOpen, setEditResourceDialogOpen] = useState(false);
  const [editDatabaseDialogOpen, setEditDatabaseDialogOpen] = useState(false);
  const [deleteResourceDialogOpen, setDeleteResourceDialogOpen] = useState(false);
  const [deleteDatabaseDialogOpen, setDeleteDatabaseDialogOpen] = useState(false);
  const [resourceToDelete, setResourceToDelete] = useState(null);
  const [databaseToDelete, setDatabaseToDelete] = useState(null);
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
  const [newDatabase, setNewDatabase] = useState({
    name: '',
    type: 'sqlite',
    host: 'localhost',
    port: 0,
    database: '',
    username: '',
    password: '',
    is_active: true,
    max_connections: 10,
    timeout: 30
  });
  const [editResource, setEditResource] = useState({
    name: '',
    uri: '',
    server_name: '',
    description: ''
  });
  const [editDatabase, setEditDatabase] = useState({
    name: '',
    type: 'sqlite',
    host: 'localhost',
    port: 0,
    database: '',
    username: '',
    password: '',
    is_active: true,
    max_connections: 10,
    timeout: 30
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

  // Fetch databases
  const { data: databasesData } = useQuery({
    queryKey: ['databases'],
    queryFn: () => api.get('/api/databases/'),
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

  // Database management mutations
  const createDatabaseMutation = useMutation({
    mutationFn: (databaseData) => api.post('/api/databases/', databaseData),
    onSuccess: () => {
      setAddDatabaseDialogOpen(false);
      setNewDatabase({
        name: '',
        type: 'sqlite',
        host: 'localhost',
        port: 0,
        database: '',
        username: '',
        password: '',
        is_active: true,
        max_connections: 10,
        timeout: 30
      });
      queryClient.invalidateQueries(['databases']);
    },
  });

  const updateDatabaseMutation = useMutation({
    mutationFn: ({ databaseName, databaseData }) => 
      api.put(`/api/databases/${databaseName}`, databaseData),
    onSuccess: () => {
      setEditDatabaseDialogOpen(false);
      queryClient.invalidateQueries(['databases']);
    },
  });

  const deleteDatabaseMutation = useMutation({
    mutationFn: (databaseName) => api.delete(`/api/databases/${databaseName}`),
    onSuccess: () => {
      setDeleteDatabaseDialogOpen(false);
      setDatabaseToDelete(null);
      queryClient.invalidateQueries(['databases']);
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

  // Database-specific helper functions
  const getDatabaseIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'postgresql':
        return <PostgreSQLIcon />;
      case 'sqlite':
        return <SQLiteIcon />;
      case 'mysql':
        return <MySQLIcon />;
      default:
        return <DatabaseIcon />;
    }
  };

  const getDatabaseColor = (type) => {
    switch (type.toLowerCase()) {
      case 'postgresql':
        return 'primary';
      case 'sqlite':
        return 'secondary';
      case 'mysql':
        return 'success';
      default:
        return 'default';
    }
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

  // Database management handlers
  const handleAddDatabase = () => {
    createDatabaseMutation.mutate(newDatabase);
  };

  const handleDeleteDatabase = (database) => {
    setDatabaseToDelete(database);
    setDeleteDatabaseDialogOpen(true);
  };

  const handleConfirmDeleteDatabase = () => {
    if (databaseToDelete) {
      deleteDatabaseMutation.mutate(databaseToDelete.name);
    }
  };

  const handleEditDatabase = (database) => {
    setEditDatabase({
      name: database.name,
      type: database.type,
      host: database.host,
      port: database.port,
      database: database.database,
      username: database.username || '',
      password: database.password || '',
      is_active: database.is_active,
      max_connections: database.max_connections || 10,
      timeout: database.timeout || 30
    });
    setEditDatabaseDialogOpen(true);
  };

  const handleUpdateDatabase = () => {
    if (editDatabase.name && editDatabase.type && editDatabase.database) {
      updateDatabaseMutation.mutate({
        databaseName: editDatabase.name,
        databaseData: editDatabase
      });
    }
  };

  const handleTypeChange = (type) => {
    const updates = { type };
    
    // Set default values based on database type
    switch (type) {
      case 'postgresql':
        updates.port = 5432;
        updates.username = 'postgres';
        updates.password = 'mcp_hub_password';
        break;
      case 'mysql':
        updates.port = 3306;
        updates.username = 'root';
        updates.password = 'password';
        break;
      case 'sqlite':
        updates.port = 0;
        updates.host = 'localhost';
        updates.username = '';
        updates.password = '';
        break;
      default:
        // No additional updates for unknown types
        break;
    }
    
    setNewDatabase({ ...newDatabase, ...updates });
  };

  const handleEditTypeChange = (type) => {
    const updates = { type };
    
    // Set default values based on database type
    switch (type) {
      case 'postgresql':
        updates.port = 5432;
        break;
      case 'mysql':
        updates.port = 3306;
        break;
      case 'sqlite':
        updates.port = 0;
        updates.host = 'localhost';
        break;
      default:
        // No additional updates for unknown types
        break;
    }
    
    setEditDatabase({ ...editDatabase, ...updates });
  };

  // Collapsible handlers
  const handleToggleServers = () => {
    setServersExpanded(!serversExpanded);
  };

  const handleToggleResources = () => {
    setResourcesExpanded(!resourcesExpanded);
  };

  const handleToggleDatabases = () => {
    setDatabasesExpanded(!databasesExpanded);
  };

  const handleToggleServerResources = (serverName) => {
    setExpandedServers(prev => ({
      ...prev,
      [serverName]: !prev[serverName]
    }));
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
          Resources & Databases
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
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setAddResourceDialogOpen(true)}
            size="small"
          >
            Add Resource
          </Button>
          <Button
            variant="outlined"
            startIcon={<DatabaseIcon />}
            onClick={() => setAddDatabaseDialogOpen(true)}
            size="small"
          >
            Add Database
          </Button>
        </Box>
      </Box>
      
      {/* Servers Section */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ mb: 2 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              p: 2,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover'
              }
            }}
            onClick={handleToggleServers}
          >
            <Box sx={{ 
              width: 4, 
              height: 24, 
              bgcolor: 'primary.main', 
              borderRadius: 2, 
              mr: 2 
            }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                MCP Servers
              </Typography>
              <Typography variant="body2" color="text.secondary">
                External MCP servers that provide tools and resources to your applications
              </Typography>
            </Box>
            <IconButton>
              {serversExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Card>
        
        <Collapse in={serversExpanded}>
        {serversData?.servers && serversData.servers.length > 0 ? (
          <Grid container spacing={3}>
            {serversData.servers.map((server) => (
              <Grid item xs={12} sm={6} md={4} key={server.name}>
                <Card 
                  sx={{ 
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ mr: 2, color: 'primary.main' }}>
                        <StorageIcon />
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {server.name}
                        </Typography>
                        <Chip
                          label={server.enabled ? 'Enabled' : 'Disabled'}
                          color={server.enabled ? 'success' : 'default'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {server.uri}
                    </Typography>
                    
                    {server.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {server.description}
                      </Typography>
                    )}
                    
                    <Button
                      variant="outlined"
                      startIcon={<SettingsIcon />}
                      fullWidth
                      sx={{ borderRadius: 2 }}
                    >
                      Manage Server
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ 
            p: 4, 
            textAlign: 'center', 
            border: '2px dashed', 
            borderColor: 'grey.300', 
            borderRadius: 2,
            bgcolor: 'grey.50'
          }}>
            <StorageIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              No MCP Servers Found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add your first MCP server to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setAddServerDialogOpen(true)}
            >
              Add Server
            </Button>
          </Box>
        )}
        </Collapse>
      </Box>

      {/* Resources Section */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ mb: 2 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              p: 2,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover'
              }
            }}
            onClick={handleToggleResources}
          >
            <Box sx={{ 
              width: 4, 
              height: 24, 
              bgcolor: 'secondary.main', 
              borderRadius: 2, 
              mr: 2 
            }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                MCP Resources
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Data sources and resources exposed through MCP servers for tool access
              </Typography>
            </Box>
            <IconButton>
              {resourcesExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Card>
        
        <Collapse in={resourcesExpanded}>
        {/* Breadcrumb-style Resources */}
        {serversData?.servers && serversData.servers.length > 0 ? (
          <Box>
            {serversData.servers.map((server) => {
              const serverResources = resources.filter(resource => resource.server === server.name);
              const isServerExpanded = expandedServers[server.name] || false;
              
              return (
                <Box key={server.name} sx={{ mb: 3 }}>
                  {/* Server Header - Collapsible */}
                  <Card sx={{ mb: 2 }}>
                    <Box 
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        p: 2,
                        cursor: 'pointer',
                        bgcolor: 'primary.50',
                        '&:hover': {
                          bgcolor: 'primary.100'
                        }
                      }}
                      onClick={() => handleToggleServerResources(server.name)}
                    >
                      <StorageIcon sx={{ mr: 2, color: 'primary.main' }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                          {server.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {server.uri}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={server.enabled ? 'Enabled' : 'Disabled'}
                          color={server.enabled ? 'success' : 'default'}
                          size="small"
                        />
                        <IconButton size="small">
                          {isServerExpanded ? <ExpandLessIcon /> : <ChevronRightIcon />}
                        </IconButton>
                      </Box>
                    </Box>
                  </Card>
                  
                  {/* Resources under this server - Collapsible */}
                  <Collapse in={isServerExpanded}>
                    {serverResources.length > 0 ? (
                      <Grid container spacing={2} sx={{ ml: 2 }}>
                        {serverResources.map((resource) => (
                        <Grid item xs={12} sm={6} md={4} key={resource.name}>
                          <Card 
                            sx={{ 
                              height: '100%', 
                              cursor: 'pointer',
                              transition: 'transform 0.2s',
                              border: '1px solid',
                              borderColor: 'grey.200',
                              '&:hover': {
                                transform: 'translateY(-2px)',
                                boxShadow: 2,
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
                              
                              {resource.description && (
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                  {resource.description}
                                </Typography>
                              )}
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
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
                    ) : (
                    <Box sx={{ 
                      p: 3, 
                      textAlign: 'center', 
                      border: '2px dashed', 
                      borderColor: 'grey.300', 
                      borderRadius: 2,
                      bgcolor: 'grey.50',
                      ml: 2
                    }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        No resources found for this server
                      </Typography>
                      <Button
                        variant="outlined"
                        startIcon={<AddIcon />}
                        onClick={() => setAddResourceDialogOpen(true)}
                        size="small"
                      >
                        Add Resource
                      </Button>
                      </Box>
                    )}
                  </Collapse>
                </Box>
              );
            })}
          </Box>
        ) : (
          <Box sx={{ 
            p: 4, 
            textAlign: 'center', 
            border: '2px dashed', 
            borderColor: 'grey.300', 
            borderRadius: 2,
            bgcolor: 'grey.50'
          }}>
            <StorageIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              No Resources Found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add a server first, then add resources to it
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setAddServerDialogOpen(true)}
              >
                Add Server
              </Button>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setAddResourceDialogOpen(true)}
              >
                Add Resource
              </Button>
            </Box>
          </Box>
        )}
        </Collapse>
      </Box>

      {/* Databases Section */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ mb: 2 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              p: 2,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover'
              }
            }}
            onClick={handleToggleDatabases}
          >
            <Box sx={{ 
              width: 4, 
              height: 24, 
              bgcolor: 'success.main', 
              borderRadius: 2, 
              mr: 2 
            }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Direct Database Connections
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Direct connections to databases for querying and data management
              </Typography>
            </Box>
            <IconButton>
              {databasesExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Card>
        
        <Collapse in={databasesExpanded}>
        {databasesData && databasesData.length > 0 ? (
          <Grid container spacing={3}>
            {databasesData.map((database) => (
              <Grid item xs={12} sm={6} md={4} key={database.name}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                    },
                  }}
                  onClick={() => {
                    setSelectedResource({
                      name: database.name,
                      uri: `${database.type}://${database.host}:${database.port}/${database.database}`
                    });
                    setQueryDialogOpen(true);
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ mr: 2, color: `${getDatabaseColor(database.type)}.main` }}>
                        {getDatabaseIcon(database.type)}
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {database.name}
                        </Typography>
                        <Chip
                          label={database.type.toUpperCase()}
                          color={getDatabaseColor(database.type)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {database.host}:{database.port}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {database.database}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Chip
                        label={database.is_active ? 'Active' : 'Inactive'}
                        color={database.is_active ? 'success' : 'default'}
                        size="small"
                        icon={database.is_active ? <CheckCircleIcon /> : <ErrorIcon />}
                      />
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Edit Database">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditDatabase(database);
                            }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Database">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDatabase(database);
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
                      Query Database
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ 
            p: 4, 
            textAlign: 'center', 
            border: '2px dashed', 
            borderColor: 'grey.300', 
            borderRadius: 2,
            bgcolor: 'grey.50'
          }}>
            <DatabaseIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              No Databases Found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add your first database connection
            </Typography>
            <Button
              variant="contained"
              startIcon={<DatabaseIcon />}
              onClick={() => setAddDatabaseDialogOpen(true)}
            >
              Add Database
            </Button>
          </Box>
        )}
        </Collapse>
      </Box>

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

      {/* Add Database Dialog */}
      <Dialog open={addDatabaseDialogOpen} onClose={() => setAddDatabaseDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Database</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Database Name"
                value={newDatabase.name}
                onChange={(e) => setNewDatabase({ ...newDatabase, name: e.target.value })}
                placeholder="e.g., production_db, analytics_db"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Database Type</InputLabel>
                <Select
                  value={newDatabase.type}
                  onChange={(e) => handleTypeChange(e.target.value)}
                  label="Database Type"
                >
                  <MenuItem value="sqlite">SQLite</MenuItem>
                  <MenuItem value="postgresql">PostgreSQL</MenuItem>
                  <MenuItem value="mysql">MySQL</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Host"
                value={newDatabase.host}
                onChange={(e) => setNewDatabase({ ...newDatabase, host: e.target.value })}
                disabled={newDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={newDatabase.port}
                onChange={(e) => setNewDatabase({ ...newDatabase, port: parseInt(e.target.value) || 0 })}
                disabled={newDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Database Name/Path"
                value={newDatabase.database}
                onChange={(e) => setNewDatabase({ ...newDatabase, database: e.target.value })}
                placeholder={newDatabase.type === 'sqlite' ? './database.db' : 'database_name'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                value={newDatabase.username}
                onChange={(e) => setNewDatabase({ ...newDatabase, username: e.target.value })}
                disabled={newDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={newDatabase.password}
                onChange={(e) => setNewDatabase({ ...newDatabase, password: e.target.value })}
                disabled={newDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Max Connections"
                type="number"
                value={newDatabase.max_connections}
                onChange={(e) => setNewDatabase({ ...newDatabase, max_connections: parseInt(e.target.value) || 10 })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Timeout (seconds)"
                type="number"
                value={newDatabase.timeout}
                onChange={(e) => setNewDatabase({ ...newDatabase, timeout: parseInt(e.target.value) || 30 })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newDatabase.is_active}
                    onChange={(e) => setNewDatabase({ ...newDatabase, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDatabaseDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAddDatabase} 
            variant="contained"
            disabled={!newDatabase.name || !newDatabase.database || createDatabaseMutation.isPending}
          >
            {createDatabaseMutation.isPending ? 'Adding...' : 'Add Database'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Database Dialog */}
      <Dialog open={editDatabaseDialogOpen} onClose={() => setEditDatabaseDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Database</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Database Name"
                value={editDatabase.name}
                disabled
                sx={{ opacity: 0.7 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Database Type</InputLabel>
                <Select
                  value={editDatabase.type}
                  onChange={(e) => handleEditTypeChange(e.target.value)}
                  label="Database Type"
                >
                  <MenuItem value="sqlite">SQLite</MenuItem>
                  <MenuItem value="postgresql">PostgreSQL</MenuItem>
                  <MenuItem value="mysql">MySQL</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Host"
                value={editDatabase.host}
                onChange={(e) => setEditDatabase({ ...editDatabase, host: e.target.value })}
                disabled={editDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={editDatabase.port}
                onChange={(e) => setEditDatabase({ ...editDatabase, port: parseInt(e.target.value) || 0 })}
                disabled={editDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Database Name/Path"
                value={editDatabase.database}
                onChange={(e) => setEditDatabase({ ...editDatabase, database: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                value={editDatabase.username}
                onChange={(e) => setEditDatabase({ ...editDatabase, username: e.target.value })}
                disabled={editDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={editDatabase.password}
                onChange={(e) => setEditDatabase({ ...editDatabase, password: e.target.value })}
                disabled={editDatabase.type === 'sqlite'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Max Connections"
                type="number"
                value={editDatabase.max_connections}
                onChange={(e) => setEditDatabase({ ...editDatabase, max_connections: parseInt(e.target.value) || 10 })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Timeout (seconds)"
                type="number"
                value={editDatabase.timeout}
                onChange={(e) => setEditDatabase({ ...editDatabase, timeout: parseInt(e.target.value) || 30 })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editDatabase.is_active}
                    onChange={(e) => setEditDatabase({ ...editDatabase, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDatabaseDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleUpdateDatabase} 
            variant="contained"
            disabled={!editDatabase.name || !editDatabase.database || updateDatabaseMutation.isPending}
          >
            {updateDatabaseMutation.isPending ? 'Updating...' : 'Update Database'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Database Dialog */}
      <Dialog open={deleteDatabaseDialogOpen} onClose={() => setDeleteDatabaseDialogOpen(false)}>
        <DialogTitle>Delete Database</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the database "{databaseToDelete?.name}"? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDatabaseDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleConfirmDeleteDatabase} 
            variant="contained" 
            color="error"
            disabled={deleteDatabaseMutation.isPending}
          >
            {deleteDatabaseMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Resources;
