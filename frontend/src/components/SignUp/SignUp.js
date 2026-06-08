import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Link, Divider } from '@mui/material';
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1';
import GitHubIcon from '@mui/icons-material/GitHub';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import GroupIcon from '@mui/icons-material/Group';
import { useNavigate } from 'react-router-dom';

const SignUp = () => {
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password || !form.confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    try {
      const res = await fetch('http://localhost:5000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        // Store user data
        localStorage.setItem('token', data.token);
        localStorage.setItem('is_admin', data.is_admin);
        localStorage.setItem('username', form.username);
        localStorage.setItem('user_id', data.user_id);
        
        // Show success message and redirect
        alert('Sign up successful! Welcome to Code Doctore.');
        navigate('/extract');
      } else {
        setError(data.error || 'Sign up failed. Please try again.');
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
          minHeight: 550,
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
          <PersonAddAlt1Icon sx={{ fontSize: 60, mb: 2, color: '#fff' }} />
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Join Code Doctore
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9, mb: 2, textAlign: 'center' }}>
            Create your free account to access advanced GitHub analytics, track developer performance, and collaborate with your team.
            <br />
            Start your journey with us today!
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <GitHubIcon sx={{ fontSize: 32, color: '#fff' }} />
            <AnalyticsIcon sx={{ fontSize: 32, color: '#fff' }} />
            <GroupIcon sx={{ fontSize: 32, color: '#fff' }} />
          </Box>
        </Box>

        {/* Right Side: Sign Up Form */}
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
            Sign Up
          </Typography>
          <Typography variant="subtitle1" align="center" sx={{ mb: 3, color: 'text.secondary' }}>
            Create your account to get started.
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              label="Username"
              name="username"
              type="text"
              fullWidth
              margin="normal"
              value={form.username}
              onChange={handleChange}
              required
            />
            <TextField
              label="Email"
              name="email"
              type="email"
              fullWidth
              margin="normal"
              value={form.email}
              onChange={handleChange}
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
              required
            />
            <TextField
              label="Confirm Password"
              name="confirmPassword"
              type="password"
              fullWidth
              margin="normal"
              value={form.confirmPassword}
              onChange={handleChange}
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
              Sign Up
            </Button>
          </form>
          {/* <Divider sx={{ my: 2 }}>or</Divider>
          <Button
            variant="outlined"
            color="primary"
            fullWidth
            startIcon={<GitHubIcon />}
            onClick={handleGitHubSignUp}
            sx={{ mb: 2, py: 1.1, fontWeight: 500 }}
          >
            Sign up with GitHub
          </Button> */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Link href="/signin" variant="body2" underline="hover">
              Already have an account?
            </Link>
            <Link href="/help" variant="body2" underline="hover">
              Need help?
            </Link>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default SignUp;
