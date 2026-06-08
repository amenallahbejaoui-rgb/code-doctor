import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Spin, Alert, Row, Col, Typography, Descriptions, Avatar, Tooltip } from 'antd';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Legend,
  LineChart, Line, CartesianGrid
} from 'recharts';
import { UserOutlined, CodeOutlined, PullRequestOutlined, IssuesCloseOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Title } = Typography;

function DeveloperAnalytics() {
  const { username, repo_id } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Group metrics by category
  const metricCategories = {
    'Code Activity': ['total_commits', 'total_lines_added', 'total_lines_removed', 'total_files_changed'],
    'Review Activity': ['total_pull_requests', 'total_reviews', 'total_comments'],
    'Issue Management': ['issues_created', 'issues_resolved', 'issues_closed']
  };

  // Metric descriptions for tooltips
  const metricDescriptions = {
    'total_commits': 'Total number of commits made to the repository',
    'total_lines_added': 'Total number of lines added across all commits',
    'total_lines_removed': 'Total number of lines removed across all commits',
    'total_files_changed': 'Total number of files modified across all commits',
    'total_pull_requests': 'Total number of pull requests created',
    'total_reviews': 'Total number of code reviews performed',
    'total_comments': 'Total number of comments made on pull requests and issues',
    'issues_created': 'Number of issues created by the developer (reporting bugs or requesting features)',
    'issues_resolved': 'Number of issues resolved by the developer (fixing bugs or implementing features)',
    'issues_closed': 'Number of issues closed by the developer (completing and verifying fixes)'
  };

  useEffect(() => {
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    fetch(`http://localhost:5000/metrics/developer_analytics/${encodeURIComponent(username)}/${repo_id}`, { headers })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Failed to fetch analytics: ${res.statusText}`);
        }
        return res.json();
      })
      .then(data => {
        if (data.error) {
          setError(data.error);
          setAnalytics(null);
        } else {
          setAnalytics(data);
        }
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [username, repo_id]);

  if (loading) return <Spin style={{ display: 'block', margin: '32px auto' }} />;
  if (error) return <Alert type="error" message={error} showIcon style={{ margin: 24 }} />;

  // Prepare data for charts
  const prepareChartData = (analytics) => {
    const chartData = {};
    
    // Initialize data structure for each category
    Object.keys(metricCategories).forEach(category => {
      chartData[category] = metricCategories[category]
        .filter(metric => analytics[metric] !== undefined)
        .map(metric => ({
          name: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value: analytics[metric]
        }));
    });

    return chartData;
  };

  const chartData = analytics ? prepareChartData(analytics) : {};

  // Custom tooltip for radar chart
  const CustomRadarTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p style={{ margin: 0 }}>{`${payload[0].name}: ${payload[0].value.toLocaleString()}`}</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const CustomBarTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p style={{ margin: 0 }}>{`${label}: ${payload[0].value.toLocaleString()}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', maxWidth: '1400px', margin: '32px auto', padding: '0 16px' }}>
      <Card 
        style={{ borderRadius: 12, boxShadow: '0 2px 16px #f0f1f2', border: 'none', marginBottom: 24 }}
      >
        <Row gutter={[24, 24]} align="middle">
          <Col xs={24} md={8} style={{ textAlign: 'center' }}>
            <Avatar 
              size={100} 
              icon={<UserOutlined />} 
              style={{ backgroundColor: '#1890ff', marginBottom: 16 }}
            />
            <Title level={3} style={{ margin: 0 }}>{username}</Title>
          </Col>
          <Col xs={24} md={16}>
            <Descriptions title="Developer Information" bordered>
              <Descriptions.Item label="Developer ID" span={3}>
                {analytics?.developer_id || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Repository" span={3}>
                {analytics?.repository_name || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Total Commits">
                {analytics?.total_commits?.toLocaleString() || '0'}
              </Descriptions.Item>
              <Descriptions.Item label="Pull Requests">
                {analytics?.total_pull_requests?.toLocaleString() || '0'}
              </Descriptions.Item>
              <Descriptions.Item label="Issues">
                {analytics?.total_issues?.toLocaleString() || '0'}
              </Descriptions.Item>
            </Descriptions>
          </Col>
        </Row>
      </Card>

      <Card 
        title={<Title level={3} style={{ margin: 0 }}>Activity Analytics</Title>}
        style={{ borderRadius: 12, boxShadow: '0 2px 16px #f0f1f2', border: 'none' }}
      >
        {analytics ? (
          <>
            {/* Summary Cards */}
            <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
              {Object.entries(metricCategories).map(([category, metrics]) => (
                <Col key={category} xs={24} sm={12} md={8}>
                  <Card 
                    title={
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {category === 'Code Activity' && <CodeOutlined />}
                        {category === 'Review Activity' && <PullRequestOutlined />}
                        {category === 'Issue Management' && <IssuesCloseOutlined />}
                        {category}
                      </div>
                    }
                    style={{ 
                      borderRadius: 8,
                      boxShadow: '0 2px 8px #f0f1f2',
                      height: '100%'
                    }}
                  >
                    {metrics.map(metric => {
                      const value = analytics[metric];
                      if (value === undefined) return null;
                      return (
                        <div key={metric} style={{ marginBottom: 8 }}>
                          <div style={{ color: '#666', fontSize: '0.9em' }}>
                            {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            <Tooltip title={metricDescriptions[metric]}>
                              <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
                            </Tooltip>
                          </div>
                          <div style={{ 
                            fontSize: '1.2em', 
                            fontWeight: 'bold',
                            color: '#1890ff'
                          }}>
                            {typeof value === 'number' ? value.toLocaleString() : value}
                          </div>
                        </div>
                      );
                    })}
                  </Card>
                </Col>
              ))}
            </Row>

            {/* Charts */}
            <Row gutter={[32, 32]}>
              {/* Radar Chart */}
              <Col xs={24} lg={12}>
                <Card title="Activity Overview" style={{ borderRadius: 8 }}>
                  <div style={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={chartData['Code Activity']}>
                        <PolarGrid stroke="#e6e6e6" />
                        <PolarAngleAxis 
                          dataKey="name" 
                          tick={{ fill: '#666' }}
                        />
                        <PolarRadiusAxis 
                          tick={{ fill: '#666' }}
                          angle={30}
                          domain={[0, 'auto']}
                        />
                        <Radar 
                          name="Activity" 
                          dataKey="value" 
                          stroke="#1890ff" 
                          fill="#1890ff" 
                          fillOpacity={0.6}
                        />
                        <Tooltip content={<CustomRadarTooltip />} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </Col>

              {/* Bar Chart */}
              <Col xs={24} lg={12}>
                <Card title="Review Activity" style={{ borderRadius: 8 }}>
                  <div style={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData['Review Activity']}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="name" 
                          tick={{ fill: '#666' }}
                          angle={-45}
                          textAnchor="end"
                          height={70}
                        />
                        <YAxis tick={{ fill: '#666' }} />
                        <Tooltip content={<CustomBarTooltip />} />
                        <Bar 
                          dataKey="value" 
                          fill="#52c41a"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </Col>

              {/* Line Chart for Trends */}
              <Col xs={24}>
                <Card title="Code Activity Trends" style={{ borderRadius: 8 }}>
                  <div style={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData['Code Activity']}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="name" 
                          tick={{ fill: '#666' }}
                        />
                        <YAxis tick={{ fill: '#666' }} />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#1890ff" 
                          strokeWidth={2}
                          dot={{ fill: '#1890ff', strokeWidth: 2 }}
                          activeDot={{ r: 8 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </Col>
            </Row>
          </>
        ) : (
          <Alert 
            type="info" 
            message="No analytics data available" 
            description="There is no analytics data available for this developer."
            showIcon 
          />
        )}
      </Card>
    </div>
  );
}

export default DeveloperAnalytics;