import React, { useEffect, useRef, useState } from 'react';
import { Menu } from 'antd';
import { Link, useParams, useLocation, useNavigate } from 'react-router-dom';
import RecommandationExample from './Recommandation/Recommandation';

const Sidebar = ({ repo: propRepo }) => {
  const { repo_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [repo, setRepo] = useState(propRepo || null);
  const lastRepoId = useRef(repo_id);

  // Determine selected key based on current path
  const getSelectedKey = () => {
    if (location.pathname.includes('/dashboard/')) return '1';
    if (location.pathname.includes('/recommandation/')) return '2';
    if (location.pathname.includes('/developer-performance/')) return '3';
    return '';
  };

  useEffect(() => {
    // Only fetch repo if repo_id changes or repo is not set
    if (!propRepo && repo_id && (repo === null || lastRepoId.current !== repo_id)) {
      const token = localStorage.getItem('token');
      fetch(`http://localhost:5000/repo/${repo_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
        .then(res => res.json())
        .then(data => {
          if (!data.error) setRepo(data);
        });
      lastRepoId.current = repo_id;
    } else if (propRepo) {
      setRepo(propRepo);
      lastRepoId.current = propRepo.id;
    }
    // eslint-disable-next-line
  }, [propRepo, repo_id]);

  // Logout logic here
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/');
  };

  return (
    <>
      <Menu
        mode="inline"
        selectedKeys={[getSelectedKey()]}
        style={{ height: '100%', borderRight: 0 }}
      >
        <Menu.Item key="repoName" disabled>
          {repo && repo.name ? repo.name : 'Repository'}
        </Menu.Item>
        <Menu.Item key="1">
          <Link to={`/dashboard/${repo?.id || repo_id}`}>Dashboard</Link>
        </Menu.Item>
        <Menu.Item key="2">
          <Link to={`/recommandation/${repo?.id || repo_id}`}>Recommandation</Link>
        </Menu.Item>
        <Menu.Item key="3">
          <Link to={`/developer-performance/${repo?.id || repo_id}`}>Developer Performance</Link>
        </Menu.Item>
        <Menu.Item key="4" onClick={handleLogout}>
          Logout
        </Menu.Item>
      </Menu>
      {/* Example Recommendation Section */}
      <RecommandationExample />
    </>
  );
};

export default Sidebar;