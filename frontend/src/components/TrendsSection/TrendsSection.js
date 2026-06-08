import React, { useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import AOS from 'aos';
import 'aos/dist/aos.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const activityData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Commits',
      data: [12, 19, 3, 5, 2, 3],
      borderColor: '#1890ff',
      fill: false,
    },
    {
      label: 'Pull Requests',
      data: [2, 3, 20, 5, 1, 4],
      borderColor: '#52c41a',
      fill: false,
    },
  ],
};

const linesData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Lines Added',
      data: [150, 200, 180, 220, 170, 210],
      borderColor: '#f59e42',
      fill: false,
    },
    {
      label: 'Lines Removed',
      data: [50, 80, 60, 90, 40, 70],
      borderColor: '#ef4444',
      fill: false,
    },
  ],
};

const performanceData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Velocity',
      data: [20, 25, 18, 30, 22, 28],
      borderColor: '#7c3aed',
      fill: false,
    },
    {
      label: 'Developer Performance',
      data: [80, 85, 78, 90, 82, 88],
      borderColor: '#38bdf8',
      fill: false,
    },
  ],
};

const TrendsSection = () => {
  useEffect(() => {
    AOS.init({ duration: 800, once: true });
  }, []);

  return (
    <section style={{ padding: '40px 0', background: '#fff' }} data-aos="fade-up">
      <h2 style={{ textAlign: 'center', fontSize: 28, fontWeight: 600, marginBottom: 32 }}>
        Activity Trends
      </h2>
      <div style={{ width: 1500, maxWidth: '100%', margin: '0 auto', marginBottom: 50,marginLeft:200 }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 60 }}>
          <div style={{ width: 700, minWidth: 400 }} data-aos="zoom-in">
            <Line data={activityData} />
          </div>
          <div style={{ width: 700, minWidth: 400 }} data-aos="zoom-in">
            <Line data={linesData} />
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'center',marginLeft:400 }}>
        <div style={{ width: 900, minWidth: 400 }} data-aos="zoom-in">
          <Line data={performanceData} />
        </div>
      </div>
    </section>
  );
};

export default TrendsSection;
