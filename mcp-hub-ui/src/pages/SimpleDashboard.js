import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

function SimpleDashboard() {
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Simple Dashboard
        </Typography>
        <Typography variant="body1">
          This is a simplified dashboard to test navigation.
        </Typography>
      </Paper>
    </Box>
  );
}

export default SimpleDashboard;
