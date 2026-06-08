import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Link, Divider } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import GitHubIcon from '@mui/icons-material/GitHub';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import GroupIcon from '@mui/icons-material/Group';
import { useNavigate } from 'react-router-dom';

const SignIn = () => {
  const [form, setForm] = useState({ identifier: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.identifier || !form.password) {
      setError('Please enter your email/username and password.');
      return;
    }
    try {
      const res = await fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.identifier,
          email: form.identifier,
          password: form.password,
        }),
      });
      const data = await res.json();
      if (res.ok && data.data) {  // Check for data in response
        // Store user data
        localStorage.setItem('token', data.data.token);
        localStorage.setItem('username', data.data.username);
        localStorage.setItem('is_admin', data.data.is_admin);
        localStorage.setItem('email', data.data.email);
        
        // Debug logs
        console.log('Login successful. Received data:', data);
        console.log('is_admin value from backend:', data.data.is_admin);
        console.log('is_admin type from backend:', typeof data.data.is_admin);
        console.log('is_admin stored in localStorage:', localStorage.getItem('is_admin'));
        console.log('Checking if is_admin is strictly true:', data.data.is_admin === true);
        
        // Redirect based on admin status
        if (data.data.is_admin === true) {
          console.log('Redirecting to admin dashboard');
          navigate('/admin-dashboard');
        } else {
          console.log('Redirecting to extract page');
          navigate('/extract');
        }
      } else {
        setError(data.message || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError('Network error. Please try again later.');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1976d2 0%, #90caf9 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Paper
        elevation={8}
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          width: { xs: '95%', md: 900 },
          minHeight: 500,
          borderRadius: 4,
          overflow: 'hidden',
        }}
      >
        {/* Left Side: Project Description & Branding */}
        <Box
          sx={{
            background: 'linear-gradient(135deg, #1565c0 0%, #42a5f5 100%)',
            color: '#fff',
            flex: 1.2,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: 5,
            gap: 3,
          }}
        >
          <LockOutlinedIcon sx={{ fontSize: 60, mb: 2, color: '#fff' }} />
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Welcome to Code Doctore
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9, mb: 2, textAlign: 'center' }}>
            Your all-in-one platform for GitHub analytics, developer performance, and team collaboration.
            <br />
            Sign in to unlock powerful insights and manage your projects efficiently.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <GitHubIcon sx={{ fontSize: 32, color: '#fff' }} />
            <AnalyticsIcon sx={{ fontSize: 32, color: '#fff' }} />
            <GroupIcon sx={{ fontSize: 32, color: '#fff' }} />
          </Box>
        </Box>

        {/* Right Side: Sign In Form */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            p: { xs: 3, md: 5 },
            background: '#fff',
          }}
        >
          <Typography variant="h5" align="center" sx={{ fontWeight: 700, color: '#1976d2', mb: 1 }}>
            Sign In
          </Typography>
          <Typography variant="subtitle1" align="center" sx={{ mb: 3, color: 'text.secondary' }}>
            Welcome back! Please sign in to your account.
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              label="Email or Username"
              name="identifier"
              type="text"
              fullWidth
              margin="normal"
              value={form.identifier}
              onChange={handleChange}
              autoComplete="username"
              required
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              fullWidth
              margin="normal"
              value={form.password}
              onChange={handleChange}
              autoComplete="current-password"
              required
            />
            {error && (
              <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                {error}
              </Typography>
            )}
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              sx={{ mt: 3, mb: 1, py: 1.2, fontWeight: 600, fontSize: 16 }}
            >
              Sign In
            </Button>
          </form>
          {/* <Divider sx={{ my: 2 }}>or</Divider>
          <Button
            variant="outlined"
            color="primary"
            fullWidth
            startIcon={<GitHubIcon />}
            onClick={handleGitHubSignIn}
            sx={{ mb: 2, py: 1.1, fontWeight: 500 }}
          >
            Sign in with GitHub
          </Button> */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Link href="/forgot-password" variant="body2" underline="hover">
              Forgot password?
            </Link>
            <Link
              component="button"
              variant="body2"
              underline="hover"
              onClick={() => navigate('/signup')}
            >
              Create account
            </Link>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default SignIn;