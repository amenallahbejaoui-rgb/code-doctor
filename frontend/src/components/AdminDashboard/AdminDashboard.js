import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Button, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Drawer, List, ListItem, ListItemIcon, ListItemText,
  AppBar, Toolbar, Avatar, Divider, Grid
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate } from 'react-router-dom';

const drawerWidth = 220;

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const adminUsername = localStorage.getItem('username');

  useEffect(() => {
    // Check if user is admin
    const isAdmin = localStorage.getItem('is_admin') === 'true';
    if (!isAdmin) {
      navigate('/signin');
      return;
    }
    fetchUsers();
  }, [navigate]);

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:5000/auth/admin/users', {
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('token'),
        },
      });
      const data = await res.json();
      if (res.ok) {
        setUsers(data.data); // <-- Use data.data, not data
      } else {
        setError(data.error || 'Failed to fetch users');
      }
    } catch {
      setError('Network error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      const res = await fetch(`http://localhost:5000/auth/admin/users/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('token'),
        },
      });
      const data = await res.json();
      if (res.ok) {
        setUsers(users.filter((u) => u.id !== id));
      } else {
        setError(data.error || 'Delete failed');
      }
    } catch {
      setError('Network error');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('is_admin');
    navigate('/signin');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f4f6fa' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            color: '#fff',
            border: 0,
          },
        }}
      >
        <Toolbar sx={{ minHeight: 80 }}>
          <DashboardIcon sx={{ fontSize: 32, mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Admin Panel
          </Typography>
        </Toolbar>
        <Divider sx={{ background: 'rgba(255,255,255,0.15)' }} />
        <List>
          <ListItem selected>
            <ListItemIcon>
              <PeopleIcon sx={{ color: '#fff' }} />
            </ListItemIcon>
            <ListItemText primary="User Management" />
          </ListItem>
          {/* Add more navigation items here */}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 1, md: 4 } }}>
        {/* Top Bar */}
        <AppBar position="static" elevation={0} sx={{ background: '#fff', color: '#1976d2', mb: 4 }}>
          <Toolbar sx={{ justifyContent: 'flex-end', minHeight: 70 }}>
            <Avatar sx={{ bgcolor: '#1976d2', mr: 2 }}>{adminUsername?.charAt(0).toUpperCase()}</Avatar>
            <Typography variant="subtitle1" sx={{ mr: 3, fontWeight: 600 }}>
              {adminUsername}
            </Typography>
            <Button
              variant="outlined"
              color="error"
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
              sx={{ fontWeight: 600 }}
            >
              Logout
            </Button>
          </Toolbar>
        </AppBar>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
              <PeopleIcon sx={{ fontSize: 40, color: '#1976d2' }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {users.filter(u => u.username !== adminUsername).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Users
                </Typography>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
              <PeopleIcon sx={{ fontSize: 40, color: '#d32f2f' }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {users.filter(u => !u.is_admin && u.username !== adminUsername).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Regular Users
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* User Table */}
        <Paper sx={{ maxWidth: 1100, mx: 'auto', borderRadius: 3, boxShadow: 4, p: 2 }}>
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 700, color: '#1976d2' }}>
            User Management
          </Typography>
          {error && <Typography color="error" align="center">{error}</Typography>}
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ background: '#e3f2fd' }}>
                  <TableCell sx={{ fontWeight: 700 }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Username</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users
                  .filter(u => u.username !== adminUsername)
                  .map((u, idx) => (
                  <TableRow
                    key={u.id}
                    sx={{
                      background: idx % 2 === 0 ? '#f9fbfd' : '#fff',
                      '&:hover': { background: '#e3f2fd' },
                      transition: 'background 0.2s',
                    }}
                  >
                    <TableCell>{u.id}</TableCell>
                    <TableCell>{u.username}</TableCell>
                    <TableCell>{u.email}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="error"
                        size="small"
                        onClick={() => handleDelete(u.id)}
                        sx={{
                          fontWeight: 600,
                        }}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {users.filter(u => u.username !== adminUsername).length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                      No users found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>
    </Box>
  );
};

export default AdminDashboard;