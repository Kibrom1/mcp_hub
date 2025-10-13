import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

function SimpleChat() {
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Simple Chat Page
        </Typography>
        <Typography variant="body1">
          This is a simplified chat page to test navigation.
        </Typography>
      </Paper>
    </Box>
  );
}

export default SimpleChat;
