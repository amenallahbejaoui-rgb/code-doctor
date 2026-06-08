import React from 'react';
import { Card, Avatar, Descriptions, Typography } from 'antd';
import { UserOutlined, MailOutlined, IdcardOutlined } from '@ant-design/icons';
import Navbar from './Navbar/Navbar';

const UserProfile = () => {
  // Retrieve user info from localStorage (or fetch from API if needed)
  const username = localStorage.getItem('username');
  const email = localStorage.getItem('email') || 'user@email.com';
  const role = localStorage.getItem('role') || 'Membre';
  const avatarUrl = localStorage.getItem('avatarUrl'); // If you have a user avatar URL

  return (
    <>
      <Navbar />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 40 }}>
        <Avatar
          size={100}
          src={avatarUrl}
          icon={<UserOutlined />}
          style={{ marginBottom: 16, backgroundColor: '#1890ff' }}
        />
        <Typography.Title level={2} style={{ marginBottom: 8 }}>
          Bienvenue, {username || 'Utilisateur'} !
        </Typography.Title>
        <Descriptions
          title="Profil de l'utilisateur"
          bordered
          column={1}
          style={{ width: 400, background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 2px 8px #f0f1f2', marginBottom: 32 }}
        >
          <Descriptions.Item label={<span><IdcardOutlined /> Nom d'utilisateur</span>}>
            {username || 'Utilisateur'}
          </Descriptions.Item>
          <Descriptions.Item label={<span><MailOutlined /> Email</span>}>
            {email}
          </Descriptions.Item>
          <Descriptions.Item label={<span><UserOutlined /> Rôle</span>}>
            {role}
          </Descriptions.Item>
        </Descriptions>
      </div>
    </>
  );
};

export default UserProfile;
