import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUser } from '../services/auth';
import { getLearningPath } from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const currentUser = getUser();
      if (!currentUser) {
        navigate('/login');
        return;
      }

      setUser(currentUser);

      // Fetch user's learning path
      try {
        const path = await getLearningPath(currentUser.user_id);
        setLearningPath(path);
      } catch (error) {
        // No learning path yet - this is okay for new users
        console.log('No learning path found:', error);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = () => {
    if (!learningPath || !learningPath.stages) return 0;

    // TODO: Calculate actual progress from completed topics
    // For now, return 0
    return 0;
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || user?.user_id}!</h1>
        <p className="dashboard-subtitle">Track your learning progress and continue your journey</p>
      </div>

      {learningPath ? (
        <div className="dashboard-content">
          <div className="learning-path-card">
            <div className="card-header">
              <h2>Your Learning Path</h2>
              <span className="coverage-badge">
                {learningPath.coverage_percentage}% Coverage
              </span>
            </div>

            <div className="job-info">
              <h3>{learningPath.role_type?.replace(/_/g, ' ').toUpperCase()}</h3>
              <p className="job-description-preview">
                Based on your target job requirements
              </p>
            </div>

            <div className="progress-section">
              <div className="progress-label">
                <span>Overall Progress</span>
                <span>{calculateProgress()}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${calculateProgress()}%` }}
                ></div>
              </div>
            </div>

            <div className="path-stats">
              <div className="stat">
                <span className="stat-value">{learningPath.covered_topics?.length || 0}</span>
                <span className="stat-label">Topics Available</span>
              </div>
              <div className="stat">
                <span className="stat-value">{learningPath.uncovered_topics?.length || 0}</span>
                <span className="stat-label">Need Resources</span>
              </div>
              <div className="stat">
                <span className="stat-value">{learningPath.stages?.length || 0}</span>
                <span className="stat-label">Learning Stages</span>
              </div>
            </div>

            <div className="card-actions">
              <button
                className="btn-primary"
                onClick={() => navigate('/learning-path')}
              >
                Continue Learning →
              </button>
              <button
                className="btn-secondary"
                onClick={() => navigate('/')}
              >
                Update Job Target
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="dashboard-content">
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h2>No Learning Path Yet</h2>
            <p>Create your first personalized learning path by entering a job description.</p>
            <button
              className="btn-primary"
              onClick={() => navigate('/')}
            >
              Create Learning Path
            </button>
          </div>
        </div>
      )}

      {/* Role-specific info */}
      {user?.role === 'recruiter' && (
        <div className="recruiter-section">
          <h3>Recruiter Tools (Coming Soon)</h3>
          <p>Find and connect with qualified candidates based on their learning progress.</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
