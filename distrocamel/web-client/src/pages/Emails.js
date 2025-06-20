import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Email as EmailIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  FilterList as FilterListIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

// Mock data for development
const mockEmails = [
  {
    id: '1',
    from: 'user1@example.com',
    subject: 'Create a simple web dashboard',
    status: 'processed',
    date: '2023-06-20T10:30:00Z',
    hasAttachment: true
  },
  {
    id: '2',
    from: 'dev@test.com',
    subject: 'Generate a Python script for data processing',
    status: 'pending',
    date: '2023-06-20T09:45:00Z',
    hasAttachment: false
  },
  {
    id: '3',
    from: 'admin@domain.com',
    subject: 'Build a REST API with authentication',
    status: 'error',
    date: '2023-06-20T08:15:00Z',
    error: 'Failed to process request',
    hasAttachment: false
  },
  {
    id: '4',
    from: 'test@example.org',
    subject: 'Create a React component library',
    status: 'processed',
    date: '2023-06-19T16:20:00Z',
    hasAttachment: true
  },
  {
    id: '5',
    from: 'support@service.com',
    subject: 'Generate documentation for the API',
    status: 'processed',
    date: '2023-06-19T14:10:00Z',
    hasAttachment: false
  }
];

const Emails = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    // Simulate API call
    const fetchEmails = async () => {
      setLoading(true);
      try {
        // In a real app, this would be an API call
        // const response = await api.get('/api/emails', { params: { search: searchTerm, filter } });
        // setEmails(response.data);
        
        // Mock API response with filtering
        setTimeout(() => {
          let filteredEmails = [...mockEmails];
          
          // Apply search filter
          if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filteredEmails = filteredEmails.filter(
              email =>
                email.from.toLowerCase().includes(term) ||
                email.subject.toLowerCase().includes(term)
            );
          }
          
          // Apply status filter
          if (filter !== 'all') {
            filteredEmails = filteredEmails.filter(email => email.status === filter);
          }
          
          setEmails(filteredEmails);
          setLoading(false);
        }, 500);
      } catch (error) {
        console.error('Error fetching emails:', error);
        setLoading(false);
      }
    };

    fetchEmails();
  }, [searchTerm, filter]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = () => {
    // In a real app, this would refresh the data
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 500);
  };

  const getStatusChip = (status, error) => {
    switch (status) {
      case 'processed':
        return <Chip icon={<CheckCircleIcon />} label="Processed" color="success" size="small" />;
      case 'pending':
        return <Chip icon={<ScheduleIcon />} label="Pending" color="warning" size="small" />;
      case 'error':
        return <Chip icon={<ErrorIcon />} label={error || 'Error'} color="error" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredEmails = emails.filter(email => {
    if (filter === 'all') return true;
    return email.status === filter;
  });

  const paginatedEmails = filteredEmails.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading && emails.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Email Logs
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<EmailIcon />}
            onClick={() => {}}
          >
            New Email
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3, p: 2 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <TextField
            variant="outlined"
            size="small"
            placeholder="Search emails..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300, mr: 2 }}
          />
          <Chip
            label="All"
            onClick={() => setFilter('all')}
            color={filter === 'all' ? 'primary' : 'default'}
            variant={filter === 'all' ? 'filled' : 'outlined'}
            sx={{ mr: 1 }}
          />
          <Chip
            label="Processed"
            onClick={() => setFilter('processed')}
            color={filter === 'processed' ? 'primary' : 'default'}
            variant={filter === 'processed' ? 'filled' : 'outlined'}
            sx={{ mr: 1 }}
          />
          <Chip
            label="Pending"
            onClick={() => setFilter('pending')}
            color={filter === 'pending' ? 'primary' : 'default'}
            variant={filter === 'pending' ? 'filled' : 'outlined'}
            sx={{ mr: 1 }}
          />
          <Chip
            label="Error"
            onClick={() => setFilter('error')}
            color={filter === 'error' ? 'primary' : 'default'}
            variant={filter === 'error' ? 'filled' : 'outlined'}
          />
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>From</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={24} />
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Loading emails...
                  </Typography>
                </TableCell>
              </TableRow>
            ) : filteredEmails.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="textSecondary">
                    No emails found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedEmails.map((email) => (
                <TableRow key={email.id} hover>
                  <TableCell>{email.from}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {email.hasAttachment && (
                        <EmailIcon color="action" fontSize="small" sx={{ mr: 1 }} />
                      )}
                      {email.subject}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {getStatusChip(email.status, email.error)}
                  </TableCell>
                  <TableCell>{formatDate(email.date)}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="View Details">
                      <IconButton size="small" onClick={() => {}}>
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" onClick={() => {}} color="error">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredEmails.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

export default Emails;
