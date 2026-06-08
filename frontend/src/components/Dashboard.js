import React, { useEffect, useState } from 'react';
import {
  Layout,
  Typography,
  Row,
  Col,
  Card,
  Spin,
  Button,
  Alert
} from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { repoService } from '../services/repoService';
const { Header, Content } = Layout;
const { Title } = Typography;

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#eb2f96', '#722ed1', '#13c2c2', '#f5222d', '#a0d911'];

const Dashboard = () => {
  const { repo_id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState({});
  const [repo, setRepo] = useState(null);
  const [repoList, setRepoList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // If no repo_id in URL, fetch repo list and redirect to first repo
    if (!repo_id) {
      repoService.getRepoList()
        .then(repos => {
          if (Array.isArray(repos) && repos.length > 0) {
            navigate(`/dashboard/${repos[0].id}`, { replace: true });
          }
        })
        .catch(error => {
          console.error('Error fetching repositories:', error);
          setError('Failed to fetch repositories');
        });
      return;
    }

    setLoading(true);
    setError(null);

    // Get the token from localStorage
    const token = localStorage.getItem('token'); 
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    // Fetch repository data
    Promise.all([
      axios.get(`http://localhost:5000/metrics/repo_statistics/${repo_id}`, { headers }),
      repoService.getRepoList()
    ])
      .then(([statsResponse, repos]) => {
        setData(statsResponse.data);
        setRepoList(repos);
        const found = repos.find(r => String(r.id) === String(repo_id));
        setRepo(found || null);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Failed to fetch data');
        setLoading(false);
      });
  }, [repo_id, navigate]);

  // Prepare chart data
  const velocityData = (data.velocity || []).map(d => ({ name: d.username, value: d.days_with_commits_pct }));
  const issuesData = (data.issues_resolved || []).map(d => ({ name: d.username, value: d.issues_resolved }));
  const prCycleData = (data.pr_cycle_time || []).map(d => ({ name: d.username, value: parseFloat(d.avg_pr_cycle_time) || 0 }));
  const prReviewsData = (data.pr_reviews || []).map(d => ({ name: d.username, value: d.total_reviews }));
  const prsMergedData = (data.prs_merged || []).map(d => ({ name: d.username, value: d.prs_merged }));
  const prSizeData = (data.pr_size || []).map(d => ({ name: d.username, value: d.avg_pr_size }));

  return (
    <>
      <Header style={{ background: '#f0faff', padding: '0 32px', display: 'flex', alignItems: 'center', minHeight: 64 }}>
        {loading && (
          <Spin size="small" style={{ marginRight: 12 }} />
        )}
        <Title level={3} style={{ margin: 0, color: '#1890ff', flex: 1 }}>
          {repo ? repo.name : 'Unknown Repository'}
        </Title>
        <Button type="primary" href="/" style={{ borderRadius: 8 }}>Back to Home</Button>
      </Header>
      <Content style={{ padding: '24px 32px' }}>
        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}
        {loading ? (
          <Spin style={{ display: 'block', margin: '32px auto' }} />
        ) : (
          <>
            <Row gutter={32} style={{ marginBottom: 32 }}>
              <Col span={12}>
                <Card title="PRs Merged (Pie Chart)" bordered={false} style={{ height: 340 }}>
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie data={prsMergedData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                        {prsMergedData.map((entry, idx) => <Cell key={entry.name} fill={COLORS[idx % COLORS.length]} />)}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Velocity (Line Chart)" bordered={false} style={{ height: 340 }}>
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={velocityData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="value" stroke="#1890ff" strokeWidth={3} dot />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
            <Row gutter={32}>
              <Col span={12}>
                <Card title="Issues Resolved (Bar Chart)" bordered={false}>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={issuesData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#52c41a" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="PR Cycle Time (Bar Chart)" bordered={false}>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={prCycleData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#faad14" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
            <Row gutter={32} style={{ marginTop: 32 }}>
              <Col span={12}>
                <Card title="PR Reviews (Bar Chart)" bordered={false}>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={prReviewsData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#eb2f96" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="PR Size (Bar Chart)" bordered={false}>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={prSizeData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#722ed1" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
            {/* Recent Commits and Reviews */}
            <Row gutter={32} style={{ marginTop: 32 }}>
              <Col span={12}>
                <Card title="Recent Commits" bordered={false} style={{ maxHeight: 340, overflow: 'auto' }}>
                  <div style={{ maxHeight: 260, overflowY: 'auto' }}>
                    {(data.recent_commits || []).length === 0 ? (
                      <div style={{ color: '#888', textAlign: 'center', marginTop: 32 }}>No recent commits</div>
                    ) : (
                      (data.recent_commits || []).map((commit) => (
                        <div key={commit.id} style={{ borderBottom: '1px solid #f0f0f0', padding: '12px 0' }}>
                          <div style={{ fontWeight: 500 }}>{commit.message}</div>
                          <div style={{ fontSize: 12, color: '#888' }}>By {commit.developer} on {commit.commit_date}</div>
                        </div>
                      ))
                    )}
                  </div>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Recent Reviews Submitted" bordered={false} style={{ maxHeight: 340, overflow: 'auto' }}>
                  <div style={{ maxHeight: 260, overflowY: 'auto' }}>
                    {(data.recent_reviews || []).length === 0 ? (
                      <div style={{ color: '#888', textAlign: 'center', marginTop: 32 }}>No recent reviews</div>
                    ) : (
                      (data.recent_reviews || []).map((review) => {
                        let statusColor = '#888';
                        if (review.review_state === 'APPROVED') statusColor = '#52c41a';
                        else if (review.review_state === 'DISMISSED') statusColor = '#f5222d';
                        else if (review.review_state === 'COMMENTED') statusColor = '#faad14';
                        return (
                          <div key={review.id} style={{ borderBottom: '1px solid #f0f0f0', padding: '12px 0' }}>
                            <div style={{ fontWeight: 500 }}>PR: {review.pr_title || 'N/A'}</div>
                            <div style={{ fontSize: 13, color: statusColor, fontWeight: 600 }}>
                              By {review.reviewer} (<span style={{ color: statusColor }}>{review.review_state}</span>)
                            </div>
                            <div style={{ fontSize: 12, color: '#888' }}>{review.submitted_at}</div>
                            {review.review_body && <div style={{ fontSize: 13, color: '#333', marginTop: 4 }}>{review.review_body}</div>}
                          </div>
                        );
                      })
                    )}
                  </div>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </Content>
    </>
  );
};

export default Dashboard;


