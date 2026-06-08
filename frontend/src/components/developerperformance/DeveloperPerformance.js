import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import './DeveloperPerformance.css';
import {
  Layout,
  Typography,
  Row,
  Col,
  Card,
  Spin,
  Alert,
} from 'antd';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { ResponsiveContainer } from 'recharts';
import { repoService } from '../../services/repoService';

const { Content } = Layout;
const { Title } = Typography;

const clusterLabels = ['unactive', 'normal', 'active'];
const clusterColors = ['#f5222d', '#1890ff', '#52c41a']; // red, blue, green

function DeveloperPerformance() {
  const { repo_id } = useParams();
  const [developers, setDevelopers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [clusteringLoading, setClusteringLoading] = useState(true);
  const [clusteringError, setClusteringError] = useState(null);
  const [repo, setRepo] = useState(null);
  const [repoList, setRepoList] = useState([]);
  const [exporting, setExporting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!repo_id) return;
    setLoading(true);
    setExporting(true);
    setError(null);
    setClusteringError(null);

    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    // First, export developer metrics and wait for it to complete
    fetch('http://localhost:5000/metrics/export_developer_metrics', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ repo_id }),
    })
      .then(res => res.json())
      .then(exportData => {
        if (exportData.status === 'error') {
          throw new Error(exportData.message || exportData.error || 'Failed to export developer metrics');
        }

        // After successful export, fetch all other data in parallel
        return Promise.all([
          // 1. Fetch the CSV data
          fetch(`http://localhost:5000/repo/csv/${repo_id}`, { headers }).then(res => res.json()),
          // 2. Fetch clustering data
          axios.get(`http://localhost:5000/metrics/clustering/${repo_id}`, { headers })
            .catch(err => {
              const errorData = err.response?.data;
              let errorMessage = errorData?.error || err.message;
              
              // Add details if available
              if (errorData?.details) {
                if (errorData.details.developers) {
                  errorMessage += `\nDevelopers: ${errorData.details.developers.join(', ')}`;
                }
                if (errorData.details.raw_metrics) {
                  errorMessage += '\n\nRaw Metrics:';
                  errorData.details.raw_metrics.forEach(metric => {
                    errorMessage += `\n${metric.username}:`;
                    Object.entries(metric).forEach(([key, value]) => {
                      if (key !== 'username') {
                        errorMessage += `\n  ${key}: ${value}`;
                      }
                    });
                  });
                }
              }
              
              setClusteringError(errorMessage);
              throw new Error(errorMessage);
            }),
          // 3. Get repository data
          repoService.getRepoList()
        ]);
      })
      .then(([csvData, clusteringResponse, repos]) => {
        setDevelopers(csvData.data || []);
        setClusters(clusteringResponse.data.clusters || []);
        setRepoList(repos);
        const found = repos.find(r => String(r.id) === String(repo_id));
        setRepo(found || null);
        setLoading(false);
        setExporting(false);
        setClusteringLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setError(err.message || 'Failed to fetch data');
        setLoading(false);
        setExporting(false);
        setClusteringLoading(false);
      });
  }, [repo_id]);

  // Helper to get cluster for a developer
  const getDevCluster = (username) => {
    const found = clusters.find(c => c.username === username);
    return found ? found.cluster : null;
  };
  const getClusterLabel = idx => clusterLabels[idx] || `Cluster ${idx}`;
  const getClusterColor = idx => clusterColors[idx] || '#8884d8';

  if (loading || exporting || !repo) return <div className="dev-perf-loading">Loading...</div>;
  if (error) return <div className="dev-perf-error">{error}</div>;

  // Prepare data for scatter plot: username on x-axis, total_score on y-axis
  const scatterData = clusters
    .filter(c => (c.code_score > 0 || c.review_score > 0) && typeof c.total_score !== 'undefined')
    .map((c, i) => ({
      x: c.username || `Dev${i + 1}`,
      y: c.total_score, // Use total_score for clustering visualization
      cluster: c.cluster,
      username: c.username || `Dev${i + 1}`,
    }));

  return (
    <>
      <Content style={{ margin: 0, padding: 32, background: '#f6faff', minHeight: 360 }}>
        {/* Clustering Section FIRST */}
        <Title level={3} style={{ color: '#1890ff' }}>Developer Clustering</Title>
        {clusteringLoading ? (
          <Spin style={{ display: 'block', margin: '32px auto' }} />
        ) : clusteringError ? (
          <Alert 
            type="error" 
            message="Clustering Error" 
            description={
              <div style={{ whiteSpace: 'pre-line' }}>
                {clusteringError}
              </div>
            }
            showIcon 
            style={{ marginBottom: 24 }} 
          />
        ) : (
          <Row gutter={32} style={{ marginBottom: 32 }}>
            <Col span={24}>
              <Card title="Developer Activity Clusters" bordered={false}>
                <div style={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <CartesianGrid />
                      <XAxis
                        type="category"
                        dataKey="x"
                        name="Username"
                        label={{ value: 'Username', position: 'bottom' }}
                        tick={{ fontSize: 12 }}
                        interval={0}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis
                        type="number"
                        dataKey="y"
                        name="Total Score"
                        label={{ value: 'Total Score', angle: -90, position: 'left' }}
                      />
                      <Tooltip
                        cursor={{ strokeDasharray: '3 3' }}
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div style={{ background: '#fff', border: '1px solid #ccc', padding: 8 }}>
                                <b>{d.username}</b><br />
                                Total Score: {d.y.toFixed(2)}<br />
                                Cluster: <span style={{ color: getClusterColor(d.cluster) }}>{getClusterLabel(d.cluster)}</span>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Legend />
                      {clusterLabels.map((label, idx) => (
                        <Scatter
                          key={label}
                          name={label}
                          data={scatterData.filter(d => d.cluster === idx)}
                          fill={getClusterColor(idx)}
                        />
                      ))}
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </Col>
          </Row>
        )}

        {/* Developer Cards Section */}
        <Title level={3} style={{ color: '#1890ff' }}>Developer Performance</Title>
        {error ? (
          <Alert 
            type="error" 
            message="Error" 
            description={
              <div style={{ whiteSpace: 'pre-line' }}>
                {error}
              </div>
            }
            showIcon 
            style={{ marginBottom: 24 }} 
          />
        ) : (
          <div className="dev-perf-cards">
            {developers
              .filter(dev => {
                const clusterEntry = clusters.find(c => c.username === (dev.username || dev.developer_id));
                return clusterEntry && (clusterEntry.code_score > 0 || clusterEntry.review_score > 0);
              })
              .map((dev, idx) => {
                const clusterIdx = getDevCluster(dev.username || dev.developer_id);
                const devId = dev.username || dev.developer_id;
                return (
                  <Link
                    key={idx}
                    to={`/developer/${encodeURIComponent(devId)}/${repo_id}`}
                    style={{ textDecoration: 'none' }}
                  >
                    <Card
                      style={{
                        border: `2px solid ${getClusterColor(clusterIdx)}`,
                        marginBottom: 16,
                        borderRadius: 8,
                        boxShadow: '0 2px 8px #f0f1f2',
                        cursor: 'pointer',
                        color: 'inherit'
                      }}
                      title={
                        <span style={{ color: getClusterColor(clusterIdx) }}>
                          {devId} {clusterIdx !== null && <span style={{ fontWeight: 400, fontSize: 14 }}>({getClusterLabel(clusterIdx)})</span>}
                        </span>
                      }
                    >
                      <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                        {Object.entries(dev).map(([key, value]) =>
                          key !== 'username' && key !== 'developer_id' ? (
                            <li key={key}><strong>{key.replace(/_/g, ' ')}:</strong> {value}</li>
                          ) : null
                        )}
                      </ul>
                    </Card>
                  </Link>
                );
              })}
          </div>
        )}
      </Content>
    </>
  );
}

export default DeveloperPerformance;
