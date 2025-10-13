import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  ContentCopy as CopyIcon,
  Psychology as NLPIcon,
  Build as ToolIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { socket } from '../services/websocket';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const queryClient = useQueryClient();

  // Fetch chat history
  const { data: chatHistory } = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => api.get('/api/chat/history'),
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (data) => api.post('/api/chat/', data),
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        provider: data.provider,
        model: data.model,
        tokens_used: data.tokens_used,
        response_time: data.response_time,
      }]);
      setIsTyping(false);
    },
    onError: (error) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
        isError: true,
      }]);
      setIsTyping(false);
    },
  });

  // WebSocket connection
  useEffect(() => {
    socket.connect();

    socket.on('chat_response', (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
      }]);
      setIsTyping(false);
    });

    socket.on('typing', () => {
      setIsTyping(true);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || sendMessageMutation.isPending) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Send via WebSocket for real-time
    socket.emit('chat', { content: input });

    // Also send via API for persistence
    sendMessageMutation.mutate({
      message: input,
      provider: 'openai', // Default provider
    });
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', p: 2 }}>
      {/* Chat Header */}
      <Paper sx={{ 
        p: 2, 
        borderRadius: 2, 
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        mb: 2,
        flexShrink: 0,
      }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          AI Chat Assistant
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '1.1rem' }}>
          Chat with AI and execute tools using natural language. Try: "List database tables" or "Show file contents"
        </Typography>
      </Paper>

      {/* Messages Area */}
      <Paper 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2,
          borderRadius: 2,
          backgroundColor: '#fafafa',
          minHeight: 0,
        }}
      >
        <List sx={{ maxHeight: '100%', overflow: 'auto' }}>
          {messages.map((message, index) => (
            <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start', py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, width: '100%' }}>
                <Avatar 
                  sx={{ 
                    mr: 1, 
                    bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                    width: 32,
                    height: 32,
                  }}
                >
                  {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
                </Avatar>
                <Chip
                  label={message.role === 'user' ? 'You' : 'AI Assistant'}
                  size="small"
                  color={message.role === 'user' ? 'primary' : 'secondary'}
                  sx={{ mr: 1 }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                  {formatTimestamp(message.timestamp)}
                </Typography>
                {message.role === 'assistant' && (
                  <IconButton 
                    size="small" 
                    onClick={() => copyToClipboard(message.content)}
                    sx={{ ml: 1 }}
                  >
                    <CopyIcon fontSize="small" />
                  </IconButton>
                )}
              </Box>
              
              <Box sx={{ ml: 5, width: '100%' }}>
                {message.isError ? (
                  <Alert 
                    severity="error" 
                    sx={{ 
                      mb: 1,
                      borderRadius: 2,
                      '& .MuiAlert-message': {
                        fontSize: '0.95rem',
                      }
                    }}
                  >
                    {message.content}
                  </Alert>
                ) : (
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontSize: '1rem',
                      lineHeight: 1.6,
                      color: 'text.primary',
                    }}
                  >
                    {message.content}
                  </Typography>
                )}
                
                {message.provider && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip 
                      label={`Provider: ${message.provider}`} 
                      size="small" 
                      variant="outlined"
                      color={message.provider === 'nlp-tools' ? 'success' : 'default'}
                      icon={message.provider === 'nlp-tools' ? <NLPIcon /> : <ToolIcon />}
                    />
                    {message.model && (
                      <Chip 
                        label={`Model: ${message.model}`} 
                        size="small" 
                        variant="outlined"
                      />
                    )}
                    {message.tokens_used && (
                      <Chip 
                        label={`Tokens: ${message.tokens_used}`} 
                        size="small" 
                        variant="outlined"
                      />
                    )}
                    {message.response_time && (
                      <Chip 
                        label={`${message.response_time.toFixed(2)}s`} 
                        size="small" 
                        variant="outlined"
                      />
                    )}
                    {message.provider === 'nlp-tools' && (
                      <Chip 
                        label="Natural Language Processing" 
                        size="small" 
                        color="success"
                        variant="filled"
                        icon={<NLPIcon />}
                      />
                    )}
                  </Box>
                )}
              </Box>
            </ListItem>
          ))}
          
          {isTyping && (
            <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start', py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Avatar sx={{ mr: 1, bgcolor: 'secondary.main', width: 32, height: 32 }}>
                  <BotIcon />
                </Avatar>
                <Chip label="AI Assistant" size="small" color="secondary" />
                <CircularProgress size={16} sx={{ ml: 2 }} />
              </Box>
              <Box sx={{ ml: 5 }}>
                <Typography variant="body2" color="text.secondary">
                  AI is thinking...
                </Typography>
              </Box>
            </ListItem>
          )}
          
          <div ref={messagesEndRef} />
        </List>
      </Paper>
      
      {/* Input Area */}
      <Paper sx={{ 
        p: 2, 
        borderRadius: 2, 
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        border: '1px solid',
        borderColor: 'grey.200',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        flexShrink: 0,
        mt: 2,
      }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything! Try: 'List database tables', 'Show file contents', or just chat normally..."
            variant="outlined"
            size="medium"
            disabled={sendMessageMutation.isPending}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                backgroundColor: 'white',
                '&:hover': {
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                },
                '&.Mui-focused': {
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                    borderWidth: 2,
                  },
                },
              },
            }}
          />
          <IconButton 
            color="primary" 
            onClick={handleSend} 
            disabled={!input.trim() || sendMessageMutation.isPending}
            sx={{ 
              bgcolor: 'primary.main',
              color: 'white',
              width: 48,
              height: 48,
              borderRadius: 3,
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              '&:hover': {
                bgcolor: 'primary.dark',
                transform: 'translateY(-1px)',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              },
              '&:disabled': {
                bgcolor: 'grey.300',
                color: 'grey.500',
                transform: 'none',
                boxShadow: 'none',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            {sendMessageMutation.isPending ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <SendIcon />
            )}
          </IconButton>
        </Box>
        
        {sendMessageMutation.isError && (
          <Alert severity="error" sx={{ mt: 1 }}>
            Failed to send message: {sendMessageMutation.error?.message}
          </Alert>
        )}
      </Paper>
    </Box>
  );
}

export default Chat;
