import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function SimpleLayout({ children }) {
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Simple Header */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', p: 2, mb: 2 }}>
        <Typography variant="h5" component="h1">
          MCP Hub - Simple Layout
        </Typography>
      </Box>
      
      {/* Simple Navigation */}
      <Box sx={{ p: 2, bgcolor: 'grey.100', mb: 2 }}>
        <Button onClick={() => navigate('/')} sx={{ mr: 1 }}>
          Dashboard
        </Button>
        <Button onClick={() => navigate('/chat')} sx={{ mr: 1 }}>
          Chat
        </Button>
        <Button onClick={() => navigate('/test')} sx={{ mr: 1 }}>
          Test
        </Button>
      </Box>
      
      {/* Content */}
      <Box sx={{ p: 2 }}>
        {children}
      </Box>
    </Box>
  );
}

export default SimpleLayout;
