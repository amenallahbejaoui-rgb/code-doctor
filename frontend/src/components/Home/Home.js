import React, { useEffect } from 'react';
import { Layout, Menu, Button, Row, Col, Card } from 'antd';
import {
  BarChartOutlined,
  TeamOutlined,
  FileTextOutlined,
  LoginOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import './Home.css';
import InsightsSection from '../InsightsSection/InsightsSection';
import TrendsSection from '../TrendsSection/TrendsSection';
import LeaderboardSection from '../LeaderboardSection/LeaderboardSection';
import ProductivityTipsSection from '../ProductivityTipsSection/ProductivityTipsSection';
import IntegrationSection from '../IntegrationSection/IntegrationSection';
import AOS from 'aos';
import 'aos/dist/aos.css';
import Navbar from '../Navbar/Navbar';

const { Header, Content
 } = Layout;

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  const handleStartClick = () => {
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/extract');
    } else {
      navigate('/signin');
    }
  };

  return (
    <Layout className="waydev-home" style={{ minHeight: '100vh' }}>
      <Navbar />
      <Content>
        <div className="waydev-hero" style={{ textAlign: 'center', padding: '80px 20px 40px 20px', background: '#f5f7fa' }}>
          <h1 style={{ fontSize: 48, fontWeight: 700, marginBottom: 24 }}>Analyse pour les équipes d'ingénierie</h1>
          <p style={{ fontSize: 20, color: '#555', marginBottom: 32 }}>
            Obtenez une visibilité sur le travail de votre équipe. Mesurez, améliorez et optimisez ses performances grâce à des données exploitables.
          </p>
          <Button type="primary" size="large" shape="round" onClick={handleStartClick}>
            Démarrer l'essai gratuit
          </Button>
        </div>

        <section className="waydev-features" id="features">
          <h2>Fonctionnalités Clés</h2>
          <div className="waydev-features-list">
            <div className="waydev-feature-card">
              <div className="waydev-feature-icon" style={{background: '#7c3aed'}}>
                <BarChartOutlined style={{ fontSize: 32, color: '#fff' }} />
              </div>
              <h3>Analyse de Code</h3>
              <p>Suivez les commits, les PRs et l'activité des revues de code en temps réel.</p>
            </div>
            <div className="waydev-feature-card">
              <div className="waydev-feature-icon" style={{background: '#38bdf8'}}>
                <TeamOutlined style={{ fontSize: 32, color: '#fff' }} />
              </div>
              <h3>Performance de l'Équipe</h3>
              <p>Visualisez la production, les blocages et les schémas de collaboration.</p>
            </div>
            <div className="waydev-feature-card">
              <div className="waydev-feature-icon" style={{background: '#f59e42'}}>
                <FileTextOutlined style={{ fontSize: 32, color: '#fff' }} />
              </div>
              <h3>Rapports & Analyses</h3>
              <p>Générez des rapports détaillés pour favoriser l'amélioration continue.</p>
            </div>
          </div>
        </section>

        <InsightsSection />
        <TrendsSection />
        <LeaderboardSection />
        <ProductivityTipsSection />
        <IntegrationSection />
        {/* Ajouter d'autres sections si nécessaire */}
      </Content>
      
    </Layout>
  );
};

export default Home;
