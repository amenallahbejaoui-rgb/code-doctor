import React, { useEffect } from 'react';
import { Table, Avatar, Tag } from 'antd';
import AOS from 'aos';
import 'aos/dist/aos.css';

const dataSource = [
  { key: '1', name: 'Alice', role: 'Ingénieure Frontend', email: 'alice@example.com', commits: 120, contributions: 85, avatar: 'https://randomuser.me/api/portraits/women/1.jpg', status: 'Actif' },
  { key: '2', name: 'Bob', role: 'Ingénieur Backend', email: 'bob@example.com', commits: 98, contributions: 70, avatar: 'https://randomuser.me/api/portraits/men/2.jpg', status: 'Actif' },
  { key: '3', name: 'Charlie', role: 'Développeur Fullstack', email: 'charlie@example.com', commits: 87, contributions: 60, avatar: 'https://randomuser.me/api/portraits/men/3.jpg', status: 'Inactif' },
];

const columns = [
  {
    title: '',
    dataIndex: 'avatar',
    key: 'avatar',
    render: (url) => <Avatar src={url} size={60} style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.10)', border: '2px solid #38bdf8' }} />, // avatar stylé
    width: 90,
    align: 'center',
  },
  {
    title: 'Développeur',
    dataIndex: 'name',
    key: 'name',
    render: (text, record) => (
      <div style={{ textAlign: 'left' }}>
        <div style={{ fontWeight: 700, fontSize: 20, color: '#222' }}>{text}</div>
        <div style={{ color: '#888', fontSize: 15 }}>{record.role}</div>
        <div style={{ color: '#38bdf8', fontSize: 13 }}>{record.email}</div>
      </div>
    ),
    align: 'left',
  },
  {
    title: 'Statut',
    dataIndex: 'status',
    key: 'status',
    render: (status) => status === 'Actif' ? <Tag color="green">Actif</Tag> : <Tag color="volcano">Inactif</Tag>,
    align: 'center',
  },
  {
    title: 'Commits',
    dataIndex: 'commits',
    key: 'commits',
    render: (num) => <span style={{ color: '#7c3aed', fontWeight: 700, fontSize: 20 }}>{num}</span>,
    align: 'center',
  },
  {
    title: 'Contributions',
    dataIndex: 'contributions',
    key: 'contributions',
    render: (val) => (
      <div style={{ width: 120 }}>
        <div style={{ height: 10, background: '#e5e7eb', borderRadius: 6, overflow: 'hidden', marginBottom: 2 }}>
          <div style={{ width: `${val}%`, background: '#52c41a', height: '100%' }}></div>
        </div>
        <span style={{ fontSize: 13, color: '#666', marginLeft: 4 }}>{val}%</span>
      </div>
    ),
    align: 'center',
  },
];

const LeaderboardSection = () => {
  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  return (
    <section style={{ padding: '56px 0', background: 'linear-gradient(90deg,#f5f7fa 60%,#e0e7ef 100%)' }} data-aos="fade-up">
      <h2 style={{ textAlign: 'center', fontSize: 38, fontWeight: 900, marginBottom: 44, letterSpacing: 1, color: '#222' }}>
        Classement des Contributeurs
      </h2>
      <div style={{ maxWidth: 1050, margin: '0 auto', background: '#fff', borderRadius: 28, boxShadow: '0 12px 48px rgba(44,62,80,0.15)', padding: 48, border: '1.5px solid #e0e7ef' }} data-aos="zoom-in">
        <Table
          dataSource={dataSource}
          columns={columns}
          pagination={false}
          rowClassName={() => 'leaderboard-row'}
          style={{ borderRadius: 28, overflow: 'hidden', fontSize: 17 }}
        />
      </div>
    </section>
  );
};

export default LeaderboardSection;
