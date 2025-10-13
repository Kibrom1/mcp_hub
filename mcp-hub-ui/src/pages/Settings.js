import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';

const Settings = () => {
  const [settings, setSettings] = useState({
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
    autoConnect: true,
    debugMode: false,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSave = async () => {
    setLoading(true);
    try {
      // Save settings to localStorage
      localStorage.setItem('mcp_hub_settings', JSON.stringify(settings));
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error saving settings');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field) => (event) => {
    setSettings({
      ...settings,
      [field]: event.target.value,
    });
  };

  const handleSwitchChange = (field) => (event) => {
    setSettings({
      ...settings,
      [field]: event.target.checked,
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Configuration
              </Typography>
              
              <TextField
                fullWidth
                label="API URL"
                value={settings.apiUrl}
                onChange={handleChange('apiUrl')}
                margin="normal"
                helperText="Backend API endpoint"
              />
              
              <TextField
                fullWidth
                label="WebSocket URL"
                value={settings.wsUrl}
                onChange={handleChange('wsUrl')}
                margin="normal"
                helperText="WebSocket connection endpoint"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Application Settings
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoConnect}
                    onChange={handleSwitchChange('autoConnect')}
                  />
                }
                label="Auto-connect to WebSocket"
              />
              
              <Divider sx={{ my: 2 }} />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.debugMode}
                    onChange={handleSwitchChange('debugMode')}
                  />
                }
                label="Debug Mode"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={loading}
        >
          Save Settings
        </Button>
        
        <Button
          variant="outlined"
          onClick={() => window.location.reload()}
        >
          Reset
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
