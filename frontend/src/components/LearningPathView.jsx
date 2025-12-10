import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLearningPath } from '../services/api';
import { getUser } from '../services/auth';
import StagedTreeLayout from './tree/StagedTreeLayout';
import '../styles/LearningPath.css';

const LearningPathView = ({ onClose }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLearningPath();
  }, []);

  const fetchLearningPath = async () => {
    try {
      setLoading(true);

      // Get current authenticated user
      const currentUser = getUser();
      if (!currentUser) {
        navigate('/login');
        return;
      }

      const data = await getLearningPath(currentUser.user_id);
      setLearningPath(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching learning path:', err);
      setError(
        err.response?.status === 404
          ? 'No learning path found. Please set your job profile in Settings first.'
          : 'Failed to load learning path. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="learning-path-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your learning path...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="learning-path-container">
        <div className="error-state">
          <h2>⚠️ {error}</h2>
          <button onClick={() => window.location.href = '/settings'} className="btn-primary">
            Go to Settings
          </button>
        </div>
      </div>
    );
  }

  if (!learningPath) {
    return null;
  }

  const getCoverageColor = (percentage) => {
    if (percentage >= 80) return '#10b981'; // Green
    if (percentage >= 60) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  return (
    <div className="learning-path-container">
      {onClose && (
        <button onClick={onClose} className="close-btn-top">
          ← Back
        </button>
      )}

      <header className="path-header">
        <h1>🎯 Your Personalized Learning Path</h1>
        <div className="job-info-card">
          <div className="job-title-row">
            <h2>{learningPath.role_type.replace(/_/g, ' ').toUpperCase()}</h2>
            <div
              className="coverage-badge"
              style={{ backgroundColor: getCoverageColor(learningPath.coverage_percentage) }}
            >
              {learningPath.coverage_percentage}% Coverage
            </div>
          </div>
          <p className="coverage-details">
            {learningPath.covered_topics.length} topics covered in our books,{' '}
            {learningPath.uncovered_topics.length} require external resources
          </p>
        </div>
      </header>

      {/* Staged Tree Visualization */}
      {learningPath.stages && learningPath.stages.length > 0 ? (
        <section className="tree-section">
          <div className="section-header">
            <h2>🌳 Your Learning Journey</h2>
            <p className="section-subtitle">
              Interactive topic tree showing your path to interview readiness
            </p>
          </div>

          <StagedTreeLayout
            stages={learningPath.stages}
            dependencies={learningPath.dependencies || []}
            onTopicClick={(topicName) => {
              // Find the full topic data with learning_structure from covered_topics
              const fullTopicData = learningPath.covered_topics?.find(
                t => t.topic === topicName
              );

              const topicSlug = topicName.toLowerCase().replace(/\s+/g, '-');
              navigate(`/topic/${topicSlug}`, {
                state: {
                  topicName,
                  topicData: fullTopicData // Pass full topic data including learning_structure
                }
              });
            }}
          />
        </section>
      ) : (
        <section className="empty-state">
          <div className="empty-message">
            <h3>No Learning Path Available</h3>
            <p>We couldn't generate a learning path based on your job description.</p>
            <p>This might be because the topics require resources we don't have yet.</p>
          </div>
        </section>
      )}

      {/* Summary Footer */}
      <footer className="path-footer">
        <div className="footer-content">
          <div className="footer-stats">
            <div className="stat">
              <span className="stat-value">{learningPath.stages?.length || 0}</span>
              <span className="stat-label">Learning Stages</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.covered_topics?.length || 0}</span>
              <span className="stat-label">Covered in Books</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.uncovered_topics?.length || 0}</span>
              <span className="stat-label">Need Resources</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.coverage_percentage || 0}%</span>
              <span className="stat-label">Overall Coverage</span>
            </div>
          </div>

          <div className="footer-actions">
            <button
              onClick={() => window.location.href = '/settings'}
              className="btn-secondary"
            >
              Update Job Profile
            </button>
            <button
              onClick={fetchLearningPath}
              className="btn-primary"
            >
              🔄 Refresh Path
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LearningPathView;
