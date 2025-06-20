import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpIcon from '@mui/icons-material/Help';
import { blue, grey } from '@mui/material/colors';
import { api } from './services/api';
import Dashboard from './pages/Dashboard';
import Emails from './pages/Emails';
import Deployments from './pages/Deployments';
import Settings from './pages/Settings';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: blue[700],
    },
    secondary: {
      main: grey[700],
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState('loading');
  const [error, setError] = useState(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        // In a real app, this would be an API call to your backend
        // const response = await api.get('/api/status');
        // setSystemStatus(response.data.status);
        
        // Mock response for now
        setTimeout(() => {
          setSystemStatus('operational');
        }, 1000);
      } catch (err) {
        setError('Failed to fetch system status');
        setSystemStatus('error');
        console.error('Error fetching system status:', err);
      }
    };

    fetchSystemStatus();
  }, []);

  const drawer = (
    <div>
      <Toolbar />
      <List>
        {['Dashboard', 'Emails', 'Deployments', 'Settings'].map((text, index) => (
          <ListItem 
            button 
            key={text} 
            component={Link} 
            to={`/${text.toLowerCase()}`}
            onClick={() => setMobileOpen(false)}
          >
            <ListItemIcon>
              {index === 0 ? <DashboardIcon /> : 
               index === 1 ? <MailIcon /> : 
               index === 2 ? <InboxIcon /> : 
               <SettingsIcon />}
            </ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          
          {/* App Bar */}
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                EMLLM Dashboard
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box 
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    bgcolor: systemStatus === 'operational' ? 'success.main' : 'error.main',
                    mr: 1,
                  }} 
                />
                <Typography variant="body2" color="inherit">
                  {systemStatus === 'loading' ? 'Loading...' : 
                   systemStatus === 'operational' ? 'Operational' : 'Error'}
                </Typography>
              </Box>
            </Toolbar>
          </AppBar>
          
          {/* Sidebar Drawer */}
          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            aria-label="mailbox folders"
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>
          
          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
            }}
          >
            <Toolbar /> {/* This pushes content below the AppBar */}
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
              {error && (
                <Box sx={{ mb: 3, p: 2, bgcolor: 'error.light', color: 'white', borderRadius: 1 }}>
                  {error}
                </Box>
              )}
              
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/emails" element={<Emails />} />
                <Route path="/deployments" element={<Deployments />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
