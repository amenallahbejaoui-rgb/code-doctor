import React, { useEffect } from 'react';
import { BulbOutlined, CheckCircleOutlined, ThunderboltOutlined, RocketOutlined, CodeOutlined } from '@ant-design/icons';
import AOS from 'aos';
import 'aos/dist/aos.css';

const tips = [
  { icon: <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 12, fontSize: 22 }} />, text: "Relisez le code régulièrement pour maintenir la qualité." },
  { icon: <CodeOutlined style={{ color: '#1890ff', marginRight: 12, fontSize: 22 }} />, text: "Rédigez des messages de commit clairs pour une meilleure collaboration." },
  { icon: <ThunderboltOutlined style={{ color: '#faad14', marginRight: 12, fontSize: 22 }} />, text: "Divisez les grandes pull requests en tâches plus petites et gérables." },
  { icon: <RocketOutlined style={{ color: '#7c3aed', marginRight: 12, fontSize: 22 }} />, text: "Automatisez les tâches répétitives pour gagner du temps." },
  { icon: <BulbOutlined style={{ color: '#f59e42', marginRight: 12, fontSize: 22 }} />, text: "Partagez vos connaissances avec l'équipe pour progresser ensemble." },
];

const ProductivityTipsSection = () => {
  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  return (
    <section style={{ padding: '48px 0', background: '#fff' }} data-aos="fade-up">
      <h2 style={{ textAlign: 'center', fontSize: 30, fontWeight: 700, marginBottom: 36, color: '#222' }}>
        Conseils de Productivité
      </h2>
      <ul style={{ maxWidth: 650, margin: '0 auto', listStyle: 'none', padding: 0 }}>
        {tips.map((tip, idx) => (
          <li key={idx} style={{ marginBottom: 20, fontSize: 19, display: 'flex', alignItems: 'center', background: '#f5f7fa', borderRadius: 12, padding: '14px 20px', boxShadow: '0 2px 12px rgba(44,62,80,0.07)' }} data-aos="zoom-in" data-aos-delay={idx * 100}>
            {tip.icon} {tip.text}
          </li>
        ))}
      </ul>
    </section>
  );
};

export default ProductivityTipsSection;
