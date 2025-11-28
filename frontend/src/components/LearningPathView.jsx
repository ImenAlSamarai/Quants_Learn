import { useState, useEffect } from 'react';
import { getLearningPath } from '../services/api';
import LearningStage from './LearningStage';
import '../styles/LearningPath.css';

const LearningPathView = ({ userId = 'demo_user', onClose }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedStage, setExpandedStage] = useState(0);

  useEffect(() => {
    fetchLearningPath();
  }, [userId]);

  const fetchLearningPath = async () => {
    try {
      setLoading(true);
      const data = await getLearningPath(userId);
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

      {/* Learning Stages Section */}
      {learningPath.stages && learningPath.stages.length > 0 && (
        <section className="stages-section">
          <div className="section-header">
            <h2>📚 Learning Stages</h2>
            <p className="section-subtitle">
              {learningPath.stages.length} stages designed for your target role
            </p>
          </div>

          <div className="stages-list">
            {learningPath.stages.map((stage, index) => (
              <LearningStage
                key={index}
                stage={stage}
                stageNumber={index + 1}
                isExpanded={expandedStage === index}
                onToggle={() => setExpandedStage(expandedStage === index ? -1 : index)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Covered Topics Section */}
      {learningPath.covered_topics && learningPath.covered_topics.length > 0 && (
        <section className="covered-section">
          <div className="section-header">
            <h2>✅ Topics Covered in Our Books</h2>
            <p className="section-subtitle">
              These topics are well-covered in our curated content
            </p>
          </div>

          <div className="topics-grid">
            {learningPath.covered_topics.map((topic, index) => (
              <div key={index} className="topic-card covered">
                <div className="topic-header">
                  <span className="topic-name">{topic.topic}</span>
                  <span className="confidence-badge">
                    {(topic.confidence * 100).toFixed(0)}% match
                  </span>
                </div>
                {topic.source && topic.source !== 'Unknown' && (
                  <div className="topic-source">
                    <span className="source-icon">📖</span>
                    <span className="source-text">{topic.source}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Uncovered Topics Section */}
      {learningPath.uncovered_topics && learningPath.uncovered_topics.length > 0 && (
        <section className="uncovered-section">
          <div className="section-header">
            <h2>🔗 Additional Resources Needed</h2>
            <p className="section-subtitle">
              These topics require external learning resources
            </p>
          </div>

          <div className="topics-grid">
            {learningPath.uncovered_topics.map((topic, index) => (
              <div key={index} className="topic-card uncovered">
                <div className="topic-header">
                  <span className="topic-name">{topic.topic}</span>
                  <span className="confidence-badge low">
                    {(topic.confidence * 100).toFixed(0)}% match
                  </span>
                </div>

                {topic.external_resources && topic.external_resources.length > 0 && (
                  <div className="external-resources">
                    <div className="resources-label">Recommended Resources:</div>
                    {topic.external_resources.map((resource, idx) => (
                      <a
                        key={idx}
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="resource-link"
                      >
                        <span className="resource-type">{resource.type}</span>
                        <span className="resource-name">{resource.name}</span>
                        <span className="external-icon">↗</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Summary Footer */}
      <footer className="path-footer">
        <div className="footer-content">
          <div className="footer-stats">
            <div className="stat">
              <span className="stat-value">{learningPath.stages.length}</span>
              <span className="stat-label">Learning Stages</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.covered_topics.length}</span>
              <span className="stat-label">Covered Topics</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.uncovered_topics.length}</span>
              <span className="stat-label">External Resources</span>
            </div>
            <div className="stat">
              <span className="stat-value">{learningPath.coverage_percentage}%</span>
              <span className="stat-label">Coverage</span>
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
