import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUser } from '../services/auth';
import { getLearningPath, fetchUserProgress } from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [userProgress, setUserProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpdateWarning, setShowUpdateWarning] = useState(false);

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

      // Fetch user's learning path and progress
      try {
        const path = await getLearningPath(currentUser.user_id);
        setLearningPath(path);

        // Fetch user progress data
        const progress = await fetchUserProgress(currentUser.user_id);
        setUserProgress(progress || []);
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

  const getAllTopics = () => {
    if (!learningPath || !learningPath.stages) return [];

    const topics = [];
    learningPath.stages.forEach(stage => {
      if (stage.topics && Array.isArray(stage.topics)) {
        stage.topics.forEach(topic => {
          topics.push({
            name: topic.name || topic.topic || topic,
            stage: stage.stage_name,
            priority: topic.priority || 'MEDIUM'
          });
        });
      }
    });
    return topics;
  };

  const getTopicProgress = (topicName) => {
    // Check if user has any progress on this topic
    // UserProgress might track by node_id, but topic names are strings
    // For MVP: check if topic appears in recent progress (by matching name in extra_metadata or similar)
    const hasProgress = userProgress.some(p =>
      p.extra_metadata?.topic_name?.toLowerCase().includes(topicName.toLowerCase()) ||
      p.time_spent_minutes > 0
    );
    return hasProgress;
  };

  const calculateProgress = () => {
    const topics = getAllTopics();
    if (topics.length === 0) return 0;

    // Count topics that have been started/completed
    const topicsWithProgress = topics.filter(topic => getTopicProgress(topic.name));
    return Math.round((topicsWithProgress.length / topics.length) * 100);
  };

  const formatJobTitle = () => {
    if (!learningPath) return 'Your Learning Path';

    // Try to extract job title from role_type
    if (learningPath.role_type) {
      return learningPath.role_type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }

    return 'Your Learning Path';
  };

  const handleUpdateJob = () => {
    if (learningPath) {
      // Show warning if user has existing path
      setShowUpdateWarning(true);
    } else {
      // No existing path, go straight to job input
      navigate('/');
    }
  };

  const confirmUpdateJob = () => {
    setShowUpdateWarning(false);
    navigate('/');
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
              <h3>{formatJobTitle()}</h3>
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

            {/* Topic Progress List */}
            <div className="topics-progress-section">
              <h3 className="section-heading">Required Topics</h3>
              <div className="topics-list">
                {getAllTopics().map((topic, index) => {
                  const hasProgress = getTopicProgress(topic.name);
                  return (
                    <div key={index} className="topic-item">
                      <span className={`topic-status ${hasProgress ? 'completed' : 'pending'}`}>
                        {hasProgress ? '✓' : '○'}
                      </span>
                      <div className="topic-details">
                        <span className="topic-name">{topic.name}</span>
                        <span className="topic-stage">{topic.stage}</span>
                      </div>
                      {topic.priority === 'HIGH' && (
                        <span className="priority-badge">High Priority</span>
                      )}
                    </div>
                  );
                })}
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
                onClick={handleUpdateJob}
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

      {/* Update Job Warning Modal */}
      {showUpdateWarning && (
        <div className="modal-overlay" onClick={() => setShowUpdateWarning(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Update Job Target?</h3>
            <p>
              Creating a new learning path will replace your current path. Your progress on
              completed modules will be preserved, but the topic list will be updated based on
              the new job requirements.
            </p>
            <p className="warning-text">
              <strong>Note:</strong> Currently, you can only track one job at a time.
              Multi-job support coming soon!
            </p>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setShowUpdateWarning(false)}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={confirmUpdateJob}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
