import React, { useEffect } from 'react';
import { Row, Col, Card } from 'antd';
import {
  UserOutlined,
  CodeOutlined,
  PlusSquareOutlined,
  MinusSquareOutlined,
  FileDoneOutlined,
  PullRequestOutlined,
  IssuesCloseOutlined,
  EyeOutlined
} from '@ant-design/icons';
import AOS from 'aos';
import 'aos/dist/aos.css';

const iconStyle = {
  fontSize: 32,
  color: '#fff',
};
const iconBgColors = [
  '#7c3aed', '#38bdf8', '#f59e42', '#10b981', '#ef4444', '#6366f1'
];
const insights = [
  {
    icon: <div style={{background: iconBgColors[0], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><UserOutlined style={iconStyle} /></div>,
    title: 'Developer Activity',
    description: 'See each developer’s total commits and contributions per repository.'
  },
  {
    icon: <div style={{background: iconBgColors[1], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><CodeOutlined style={iconStyle} /></div>,
    title: 'Code Changes',
    description: 'Track lines added, removed, and changed to measure code churn and productivity.'
  },
  {
    icon: <div style={{background: iconBgColors[2], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><FileDoneOutlined style={iconStyle} /></div>,
    title: 'Files Changed',
    description: 'Monitor how many files are affected by each developer’s work.'
  },
  {
    icon: <div style={{background: iconBgColors[3], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><PullRequestOutlined style={iconStyle} /></div>,
    title: 'Pull Requests',
    description: 'Count pull requests opened by each developer to understand collaboration.'
  },
  {
    icon: <div style={{background: iconBgColors[4], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><IssuesCloseOutlined style={iconStyle} /></div>,
    title: 'Issues Handled',
    description: 'See how many issues each developer is involved with.'
  },
  {
    icon: <div style={{background: iconBgColors[5], borderRadius: '50%', width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'}}><EyeOutlined style={iconStyle} /></div>,
    title: 'Code Reviews',
    description: 'Track code review activity to encourage best practices and knowledge sharing.'
  }
];

const InsightsSection = () => {
  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  return (
    <section className="waydev-insights" id="insights" style={{ padding: '60px 0', background: '#f5f7fa' }} data-aos="fade-up">
      <h2 style={{ textAlign: 'center', fontSize: 32, fontWeight: 600, marginBottom: 8 }}>
        What Insights Do We Provide?
      </h2>
      <div style={{ textAlign: 'center', color: '#7c3aed', fontSize: 18, marginBottom: 36, fontWeight: 500 }}>
        Actionable metrics to help your team grow
      </div>
      <Row gutter={[32, 32]} justify="center">
        {insights.map((insight, idx) => (
          <Col xs={24} md={8} key={idx} data-aos="zoom-in" data-aos-delay={idx * 100}>
            <Card
              hoverable
              bordered={false}
              className="waydev-insight-card"
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', minHeight: 260, height: 260, borderRadius: 18, background: 'linear-gradient(135deg, #fff 60%, #f3f4f6 100%)', boxShadow: '0 4px 24px rgba(124,58,237,0.08)', padding: 24 }}
              cover={null}
            >
              {insight.icon}
              <h3 style={{ color: '#7c3aed', fontWeight: 700, marginTop: 18 }}>{insight.title}</h3>
              <p style={{ color: '#555', fontSize: 16 }}>{insight.description}</p>
            </Card>
          </Col>
        ))}
      </Row>
    </section>
  );
};

export default InsightsSection;