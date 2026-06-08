import React from 'react';
import './App.css';
import Home from './components/Home/Home';
import Extract from './components/Extract/Extract';
import Dashboard from './components/Dashboard';
import DeveloperPerformance from './components/developerperformance/DeveloperPerformance';
import DeveloperAnalytics from './components/developerperformance/DeveloperAnalytics';
import SignIn from './components/SignIn/SignIn';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignUp from './components/SignUp/SignUp';
import AdminDashboard from './components/AdminDashboard/AdminDashboard';
import UserProfile from './components/UserProfile';
import MainLayout from './components/Layout/MainLayout';
import Recommandation, { RecommandationExample } from './components/Recommandation/Recommandation';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/extract" element={<Extract />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/user-profile" element={<UserProfile />} />
          
          {/* Routes with shared layout */}
          <Route element={<MainLayout />}>
            <Route path="/dashboard/:repo_id" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/developer-performance/:repo_id" element={<DeveloperPerformance />} />
            <Route path="/developer/:username/:repo_id" element={<DeveloperAnalytics />} />
            <Route path="/recommandation/:repo_id" element={<RecommandationExample />} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
