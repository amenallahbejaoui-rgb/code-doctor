import React from 'react';
import { Layout, Menu, Button } from 'antd';
import { LoginOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Header } = Layout;

const Navbar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username'); // Save username on login

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('is_admin');
    localStorage.removeItem('username');
    navigate('/signin');
  };

  return (
    <Header className="waydev-header" style={{ background: '#fff', boxShadow: '0 2px 8px #f0f1f2' }}>
      <div
        className="waydev-logo"
        style={{ float: 'left', fontWeight: 'bold', fontSize: 24, color: '#1890ff', cursor: 'pointer' }}
        onClick={() => navigate('/')}
      >
        Waydev
      </div>
      <Menu mode="horizontal" style={{ float: 'right', borderBottom: 'none' }}>
        <Menu.Item key="features"><a href="#features">Fonctionnalités</a></Menu.Item>
        <Menu.Item key="pricing"><a href="#pricing">Tarification</a></Menu.Item>
        <Menu.Item key="about"><a href="#about">À propos</a></Menu.Item>
        {!token ? (
          <Menu.Item
            key="login"
            icon={<LoginOutlined />}
            onClick={() => navigate('/signin')}
          >
            Connexion
          </Menu.Item>
        ) : (
          <>
            <Menu.Item
              key="user"
              icon={<UserOutlined />}
              onClick={() => navigate('/user-profile')}
              style={{ cursor: 'pointer' }}
            >
              {username || 'Utilisateur'}
            </Menu.Item>
            <Menu.Item
              key="logout"
              icon={<LogoutOutlined />}
              onClick={handleLogout}
            >
              Déconnexion
            </Menu.Item>
          </>
        )}
      </Menu>
    </Header>
  );
};

export default Navbar;