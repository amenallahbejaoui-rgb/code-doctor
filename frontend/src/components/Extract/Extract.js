import React, { useState, useEffect } from 'react';
import { Input, Button, Form, Alert, Spin, Card, Progress, Steps } from 'antd';
import axios from 'axios';
import { GithubOutlined, ArrowLeftOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import AOS from 'aos';
import 'aos/dist/aos.css';
import './Extract.css';

const { Step } = Steps;

const Extract = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [repoList, setRepoList] = useState([]);
  const [repoListLoading, setRepoListLoading] = useState(false);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const steps = [
    {
      title: 'Repository Info',
      description: 'Fetching repository details',
    },
    {
      title: 'Pull Requests',
      description: 'Extracting PR data',
    },
    {
      title: 'Reviews',
      description: 'Processing reviews',
    },
    {
      title: 'Commits',
      description: 'Analyzing commits',
    },
    {
      title: 'Developers',
      description: 'Processing contributors',
    },
    {
      title: 'Issues',
      description: 'Extracting issues',
    },
  ];

  useEffect(() => {
    AOS.init({ duration: 800, once: true });
    const fetchRepos = async () => {
      setRepoListLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No authentication token found');
          navigate('/signin');
          return;
        }

        const res = await axios.get('http://localhost:5000/repo/list', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (res.data) {
          setRepoList(res.data);
        }
      } catch (e) {
        console.error('Failed to fetch repositories:', e);
        if (e.response?.status === 401) {
          // Clear all stored data
          localStorage.clear();
          navigate('/signin');
        }
      } finally {
        setRepoListLoading(false);
      }
    };
    fetchRepos();
  }, [navigate]);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setShowResult(false);
    setExtractionProgress(0);
    setCurrentStep(0);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/signin');
        return;
      }
      const response = await axios.post(
        'http://localhost:5000/repo/process',
        { repo_url: repoUrl },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setExtractionProgress(progress);
            // Update current step based on progress
            const step = Math.floor(progress / (100 / steps.length));
            setCurrentStep(Math.min(step, steps.length - 1));
          },
        }
      );
      setResult(response.data);
      setShowResult(true);
      setExtractionProgress(100);
      setCurrentStep(steps.length - 1);
    } catch (err) {
      if (err.response?.status === 401) {
        // Clear invalid token
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        // Redirect to login
        navigate('/signin');
      } else {
        setError(err.response?.data?.error || 'An error occurred during extraction');
        setExtractionProgress(0);
        setCurrentStep(0);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setRepoUrl('');
    setResult(null);
    setError(null);
    setShowResult(false);
    setExtractionProgress(0);
    setCurrentStep(0);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(120deg, #e6f7ff 0%, #bae7ff 60%, #fff 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background circles */}
      <div style={{
        position: 'absolute',
        top: 60,
        left: 80,
        width: 220,
        height: 220,
        background: 'rgba(24,144,255,0.13)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        zIndex: 0
      }} />
      <div style={{
        position: 'absolute',
        bottom: 80,
        right: 120,
        width: 180,
        height: 180,
        background: 'rgba(82,196,26,0.13)',
        borderRadius: '50%',
        filter: 'blur(32px)',
        zIndex: 0
      }} />
      <Card
        style={{
          maxWidth: 900,
          width: '100%',
          padding: 0,
          borderRadius: 32,
          boxShadow: '0 12px 48px 0 rgba(24,144,255,0.16)',
          border: '1.5px solid #e6f7ff',
          position: 'relative',
          overflow: 'hidden',
          background: 'rgba(255,255,255,0.85)',
          backdropFilter: 'blur(8px)',
          zIndex: 1
        }}
        styles={{ body: { padding: 64 } }}
        data-aos="zoom-in"
      >
        <div style={{
          position: 'absolute',
          top: -60,
          right: -60,
          width: 180,
          height: 180,
          background: 'rgba(24,144,255,0.10)',
          borderRadius: '50%',
          zIndex: 0
        }} />
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <GithubOutlined style={{ fontSize: 60, color: '#1890ff', filter: 'drop-shadow(0 2px 12px #bae7ff)' }} />
        </div>
        <h2 style={{ textAlign: 'center', marginBottom: 18, fontWeight: 900, fontSize: 36, color: '#1890ff', letterSpacing: 1 }}>
          Extract GitHub Repository Data
        </h2>
        <div style={{ textAlign: 'center', marginBottom: 36, fontSize: 18, color: '#444', fontWeight: 500 }}>
          Enter a public GitHub repository URL to extract detailed metrics and information.
        </div>

        {/* Extraction Progress */}
        {loading && (
          <div style={{ marginBottom: 32 }}>
            <Steps current={currentStep} style={{ marginBottom: 24 }}>
              {steps.map((step, index) => (
                <Step
                  key={index}
                  title={step.title}
                  description={step.description}
                  icon={index < currentStep ? <CheckCircleOutlined /> : index === currentStep ? <LoadingOutlined /> : null}
                />
              ))}
            </Steps>
            <Progress percent={extractionProgress} status="active" />
          </div>
        )}

        {/* Repository List */}
        <div style={{ marginBottom: 44 }}>
          <h3 style={{ fontWeight: 800, color: '#1890ff', marginBottom: 16, fontSize: 22 }}>Extracted Repositories</h3>
          {repoListLoading ? (
            <Spin />
          ) : repoList.length === 0 ? (
            <div style={{ color: '#888', fontSize: 16 }}>No repositories extracted yet.</div>
          ) : (
            <div style={{ maxHeight: 220, overflowY: 'auto', marginBottom: 8, display: 'flex', gap: 18, flexWrap: 'wrap' }}>
              {repoList.map(repo => (
                <Card key={repo.id} size="small" style={{ minWidth: 260, flex: 1, marginBottom: 10, borderRadius: 12, background: '#f6ffed', border: '1px solid #b7eb8f', boxShadow: '0 2px 12px #e6fffb' }}>
                  <div style={{ fontWeight: 700, color: '#237804', fontSize: 18 }}>{repo.name}</div>
                  <div style={{ color: '#888', fontSize: 14, marginBottom: 4 }}>{repo.description}</div>
                  <div style={{ fontSize: 14, color: '#555', marginBottom: 6 }}>
                    ⭐ {repo.stars} &nbsp; | &nbsp; 🍴 {repo.forks} &nbsp; | &nbsp; 🐞 {repo.open_issues} &nbsp; | &nbsp; 📝 {repo.language}
                  </div>
                  <Button
                    type="primary"
                    size="small"
                    style={{ marginTop: 8, borderRadius: 8, fontWeight: 700, letterSpacing: 1 }}
                    onClick={() => navigate(`/dashboard/${repo.id}`)}
                    block
                  >
                    View Dashboard
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Extraction Form */}
        <Form layout="vertical" onFinish={handleSubmit} style={{ zIndex: 1, position: 'relative', maxWidth: 600, margin: '0 auto' }}>
          <Form.Item label={<span style={{ fontWeight: 700, color: '#333', fontSize: 18 }}>GitHub Repository URL</span>} required>
            <Input
              value={repoUrl}
              onChange={e => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              size="large"
              disabled={loading}
              style={{ borderRadius: 10, border: '1.5px solid #bae7ff', background: '#f0faff', fontSize: 17 }}
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" size="large" block loading={loading} disabled={!repoUrl} style={{ borderRadius: 10, fontWeight: 700, letterSpacing: 1, fontSize: 18 }}>
              Extract Data
            </Button>
            {showResult && (
              <Button onClick={handleReset} style={{ marginTop: 14, borderRadius: 10, fontWeight: 600, fontSize: 16 }} block>
                Extract Another Repository
              </Button>
            )}
          </Form.Item>
        </Form>

        {/* Error Display */}
        {error && <Alert type="error" message={error} showIcon style={{ marginTop: 18, borderRadius: 10, fontSize: 16 }} />}

        {/* Result Display */}
        {showResult && !!result && (
          <div>
            <Alert
              type="success"
              message={<span style={{ fontWeight: 700, color: '#389e0d', fontSize: 18 }}>Extraction Result</span>}
              description={<pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', maxHeight: 340, overflow: 'auto', background: '#f6ffed', borderRadius: 10, padding: 18, color: '#237804', fontSize: 16 }}>{JSON.stringify(result, null, 2)}</pre>}
              showIcon
              style={{ marginTop: 18, borderRadius: 10 }}
            />
            {result.repo_id && (
              <Button
                type="primary"
                style={{ marginTop: 18, borderRadius: 10, fontWeight: 700, fontSize: 17 }}
                block
                onClick={() => navigate(`/dashboard/${result.repo_id}`)}
              >
                View Repository Dashboard
              </Button>
            )}
          </div>
        )}

        {/* Navigation */}
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ marginTop: 40, borderRadius: 10, fontWeight: 700, fontSize: 17 }} block>
          Back to Home
        </Button>
      </Card>
    </div>
  );
};

export default Extract;
