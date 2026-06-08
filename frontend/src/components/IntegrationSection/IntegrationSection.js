import React, { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import { GithubOutlined, GitlabOutlined, BranchesOutlined } from '@ant-design/icons';

const IntegrationSection = () => {
  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  return (
    <section style={{ padding: '40px 0', background: '#f5f7fa' }} data-aos="fade-up">
      <h2 style={{ textAlign: 'center', fontSize: 28, fontWeight: 600, marginBottom: 32 }}>
        Integrations
      </h2>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 40 }} data-aos="zoom-in">
        <GithubOutlined style={{ fontSize: 48, color: '#24292e' }} />
        <GitlabOutlined style={{ fontSize: 48, color: '#fc6d26' }} />
        <BranchesOutlined style={{ fontSize: 48, color: '#205081' }} />
      </div>
      <p style={{ textAlign: 'center', marginTop: 24, fontSize: 18 }}>
        Connect your favorite code hosting platforms.
      </p>
    </section>
  );
};

export default IntegrationSection;
