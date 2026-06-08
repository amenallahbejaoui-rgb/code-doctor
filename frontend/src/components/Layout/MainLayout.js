import React from 'react';
import { Layout } from 'antd';
import { Outlet, useParams } from 'react-router-dom';
import Sidebar from '../Sidebar';
import { useState, useEffect } from 'react';
import { repoService } from '../../services/repoService';

const { Content, Sider } = Layout;

const MainLayout = () => {
  const { repo_id } = useParams();
  const [repo, setRepo] = useState(null);

  useEffect(() => {
    if (repo_id) {
      repoService.getRepoById(repo_id)
        .then(foundRepo => setRepo(foundRepo))
        .catch(error => {
          console.error('Error fetching repository:', error);
          setRepo(null);
        });
    }
  }, [repo_id]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} style={{ background: '#fff', boxShadow: '2px 0 8px #f0f1f2' }}>
        <Sidebar repo={repo} />
      </Sider>
      <Layout>
        <Content style={{ margin: 0, padding: 32, background: '#f6faff', minHeight: 360 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 